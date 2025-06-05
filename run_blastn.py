import subprocess
import argparse
import os
import sys

def check_blast_environment():
    """检查 BLAST 环境是否激活，若未激活则尝试激活"""
    try:
        result = subprocess.run(['which', 'blastn'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("BLAST 环境已激活")
            return True
        else:
            print("未找到 BLAST 环境，尝试激活...")
            try:
                subprocess.run(['conda', 'activate', 'blast'], shell=True, check=True)
                print("BLAST 环境激活成功")
                return True
            except subprocess.CalledProcessError:
                print("错误：无法激活 BLAST 环境。请确保 Conda 及 'blast' 环境已正确配置")
                return False
    except FileNotFoundError:
        print("错误：未找到 'which' 命令。请确保 BLAST 已安装并在 PATH 中")
        return False

def make_blast_db(input_fasta, db_path, db_type='nucl'):
    """使用 makeblastdb 构建 BLAST 数据库"""
    db_dir = os.path.dirname(db_path) or '.'
    os.makedirs(db_dir, exist_ok=True)
    
    makeblastdb_cmd = [
        'makeblastdb',
        '-in', input_fasta,
        '-dbtype', db_type,
        '-out', db_path
    ]
    try:
        print(f"构建 BLAST 数据库：{' '.join(makeblastdb_cmd)}")
        subprocess.run(makeblastdb_cmd, check=True)
        print(f"数据库构建完成：{db_path}")
    except subprocess.CalledProcessError as e:
        print(f"构建 BLAST 数据库时出错：{e}")
        sys.exit(1)

def filter_blast_output(output_file, min_identity):
    """根据 percent_identity 过滤 BLAST 输出文件，确保保留表头"""
    temp_file = output_file + ".temp"
    header = None
    filtered_lines = []
    
    try:
        with open(output_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # 增强表头检测，匹配包含 'query_id' 的行
                if 'query_id' in line:
                    header = line
                    continue
                fields = line.split('\t')
                if len(fields) < 3:
                    print(f"警告：跳过无效数据行：{line}")
                    continue
                try:
                    percent_identity = float(fields[2])
                    if percent_identity >= min_identity:
                        filtered_lines.append(line)
                except ValueError:
                    print(f"警告：跳过无法解析 percent_identity 的行：{line}")
                    continue
        
        with open(temp_file, 'w') as f:
            if header:
                f.write(header + '\n')
            for line in filtered_lines:
                f.write(line + '\n')
        
        os.replace(temp_file, output_file)
        print(f"已过滤输出文件，保留 percent_identity >= {min_identity} 的记录")
    except Exception as e:
        print(f"过滤 BLAST 输出时出错：{e}")
        sys.exit(1)

def run_blastn(query, output, db_path, evalue, max_target_seqs, num_threads, add_header, min_identity):
    """运行 blastn 命令并根据需要添加表头和过滤"""
    blast_cmd = [
        'blastn',
        '-query', query,
        '-out', output,
        '-db', db_path,
        '-outfmt', '6',
        '-evalue', str(evalue),
        '-max_target_seqs', str(max_target_seqs),
        '-num_threads', str(num_threads)
    ]

    try:
        print(f"运行 BLAST 命令：{' '.join(blast_cmd)}")
        subprocess.run(blast_cmd, check=True)
        print(f"BLAST 运行完成，输出保存至：{output}")

        if add_header:
            header = "query_id\tsubject_id\tpercent_identity\talignment_length\tmismatches\tgap_opens\tq.start\tq.end\ts.start\ts.end\tevalue\tbit_score"
            temp_file = output + ".temp"
            # 使用 Python 写入表头，避免 echo -e 的问题
            with open(temp_file, 'w') as f:
                f.write(header + '\n')
                with open(output, 'r') as infile:
                    f.write(infile.read())
            os.replace(temp_file, output)
            print("已为输出文件添加表头")

        if min_identity is not None:
            filter_blast_output(output, min_identity)
    except subprocess.CalledProcessError as e:
        print(f"运行 BLAST 时出错：{e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="运行 BLASTn 的 Python 脚本，支持构建数据库、比对、过滤和环境激活。",
        epilog="示例:\n"
               "  # 仅运行 BLASTn\n"
               "  python3 run_blastn.py -q rep-seqs.fa -o rep_blast.txt -d /path/to/db/all -e 1e-5 -m 3 -t 1\n"
               "  # 构建数据库并运行 BLASTn\n"
               "  python3 run_blastn.py -q Sph_CandidateASVs.fa -o 240510_28B2 -d /home/zwang/workspace/blast/db/Sphingobium_db -e 1e-5 -t 20 --header --make_db Sphingobium_isolate_16s.fasta\n"
               "  # 过滤 percent_identity >= 97\n"
               "  python3 run_blastn.py -q Sph_CandidateASVs.fa -o 240510_28B2 -d /home/zwang/workspace/blast/db/Sphingobium_db -e 1e-5 -t 20 --header --min_identity 97\n\n"
               "注意:\n"
               "  - 确保 BLAST 环境名为 'blast'，或根据需要修改脚本中的环境名称。\n"
               "  - 使用 -d 指定数据库的完整路径（包括目录和数据库名称）。\n"
               "  - 使用 --make_db 构建数据库，数据库文件将保存到 -d 指定的路径。\n"
               "  - 使用 --header 添加表头，--min_identity 过滤 percent_identity。\n"
               "  - 如果使用 --min_identity，必须启用 --header 以确保正确解析。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-q', '--query', required=True, help="输入 FASTA 文件路径（必填）")
    parser.add_argument('-o', '--output', required=True, help="输出文件路径（必填）")
    parser.add_argument('-d', '--db', required=True, help="BLAST 数据库完整路径（包括目录和数据库名称，必填）")
    parser.add_argument('-e', '--evalue', type=float, default=1e-5, help="E-value 阈值（默认：1e-5）")
    parser.add_argument('-m', '--max_target_seqs', type=int, default=3, help="最大目标序列数（默认：3）")
    parser.add_argument('-t', '--num_threads', type=int, default=1, help="线程数（默认：1）")
    parser.add_argument('--header', action='store_true', help="为输出文件添加表头（包含 query_id, subject_id, percent_identity 等列）")
    parser.add_argument('--make_db', help="构建 BLAST 数据库的输入 FASTA 文件路径（可选）")
    parser.add_argument('--min_identity', type=float, help="过滤 percent_identity 的最小阈值（例如 97 表示 >= 97）")

    args = parser.parse_args()

    if args.min_identity is not None and not args.header:
        print("错误：使用 --min_identity 时必须启用 --header")
        sys.exit(1)

    if not check_blast_environment():
        sys.exit(1)

    if args.make_db:
        make_blast_db(args.make_db, args.db)

    run_blastn(
        query=args.query,
        output=args.output,
        db_path=args.db,
        evalue=args.evalue,
        max_target_seqs=args.max_target_seqs,
        num_threads=args.num_threads,
        add_header=args.header,
        min_identity=args.min_identity
    )

if __name__ == "__main__":
    main()
