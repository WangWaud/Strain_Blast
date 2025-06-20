# BLASTn 自动化脚本 (`run_blastn.py`)

这是一个用于自动化运行 BLASTn 的 Python 脚本，支持构建 BLAST 数据库、运行比对、添加表头以及根据 `percent_identity` 过滤结果。脚本设计用于 Linux 和 macOS 环境，特别适合生物信息学分析中的序列比对任务。

## 功能
- **环境检查**：自动检测并激活 Conda 的 `blast` 环境，确保 `blastn` 和 `makeblastdb` 可用。
- **构建数据库**：使用 `makeblastdb` 根据输入 FASTA 文件创建 BLAST 数据库，支持自定义输出路径。
- **运行 BLASTn**：执行 BLASTn 比对，支持自定义参数（如 E-value、最大目标序列数、线程数）。
- **添加表头**：为 BLAST 输出（`-outfmt 6`）添加标准表头（`query_id`, `subject_id`, `percent_identity` 等）。
- **过滤结果**：根据 `percent_identity` 阈值过滤比对结果，仅保留满足条件的记录。
- **灵活路径**：支持为数据库和输出文件指定完整路径。

## 安装要求
- **操作系统**：Linux（测试于 Ubuntu）或 macOS（测试于 macOS Ventura）
- **Python**：版本 3.6 或更高（测试于 Python 3.13）
- **BLAST**：NCBI BLAST+ 工具集，安装在 Conda 环境 `blast` 中
  - 安装示例：
    ```bash
    conda create -n blast -c bioconda blast
    ```
- **依赖**：仅需 Python 标准库（`subprocess`, `argparse`, `os`, `sys`），无需额外安装模块。

## 使用方法

### 在 Linux 上运行
1. **下载脚本并移动至工作目录**：
   - 将 `run_blastn.py` 复制到你的工作目录，例如 `/path/to/workspace/blast/`.
2. **确保脚本可执行**：
   ```bash
   chmod +x run_blastn.py
   ```
3. **激活 BLAST 环境**：
   ```bash
   conda activate blast
   ```
4. **运行脚本**：
   - 基本命令：
     ```bash
     python3 run_blastn.py -q query.fa -o output.txt -d /path/to/db/my_db -e 1e-5 -m 3 -t 1
     ```
   - 查看帮助：
     ```bash
     python3 run_blastn.py -h
     ```

### 在 macOS 上运行
1. **安装 Miniconda**（若未安装）：
   - 下载 Miniconda（选择 macOS 版本，Intel 或 Apple Silicon）：
     ```bash
     curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
     bash Miniconda3-latest-MacOSX-arm64.sh
     ```
   - 初始化 Conda（假设使用 zsh）：
     ```bash
     ~/miniconda3/bin/conda init zsh
     source ~/.zshrc
     ```
2. **创建 BLAST 环境**：
   - 创建并安装 BLAST+：
     ```bash
     conda create -n blast -c bioconda blast
     ```
   - 激活环境：
     ```bash
     conda activate blast
     ```
3. **下载脚本并移动至工作目录**：
   - 将 `run_blastn.py` 复制到工作目录，例如 `/Users/username/workspace/blast/`.
4. **确保脚本可执行**：
   ```bash
   chmod +x run_blastn.py
   ```
5. **准备输入文件**：
   - 复制 FASTA 文件（如 `query.fa`, `reference.fa`）到工作目录：
     ```bash
     mkdir -p /Users/username/workspace/blast
     cp /path/to/query.fa /Users/username/workspace/blast/
     cp /path/to/reference.fa /Users/username/workspace/blast/
     ```
6. **运行脚本**：
   - 基本命令：
     ```bash
     python3 run_blastn.py -q /Users/username/workspace/blast/query.fa -o /Users/username/workspace/blast/output.txt -d /Users/username/workspace/blast/db/my_db -e 1e-5 -m 3 -t 1
     ```
   - 查看帮助：
     ```bash
     python3 run_blastn.py -h
     ```

## 参数说明
| 参数 | 描述 | 是否必填 | 默认值 |
|------|------|----------|--------|
| `-q`, `--query` | 输入 FASTA 文件路径 | 是 | 无 |
| `-o`, `--output` | 输出文件路径 | 是 | 无 |
| `-d`, `--db` | BLAST 数据库完整路径（包括目录和数据库名称） | 是 | 无 |
| `-e`, `--evalue` | E-value 阈值 | 否 | 1e-5 |
| `-m`, `--max_target_seqs` | 最大目标序列数 | 否 | 3 |
| `-t`, `--num_threads` | 线程数 | 否 | 1 |
| `--header` | 为输出文件添加表头（`query_id`, `subject_id`, `percent_identity` 等） | 否 | 不启用 |
| `--make_db` | 构建 BLAST 数据库的输入 FASTA 文件路径 | 否 | 无 |
| `--min_identity` | 过滤 `percent_identity` 的最小阈值（例如 `97` 表示 >= 97） | 否 | 无 |

**注意**：
- 使用 `--min_identity` 时必须启用 `--header`，否则脚本会报错。
- `-d` 需指定完整路径（如 `/home/user/db/my_db` 或 `/Users/username/db/my_db`），脚本会自动创建目录。

## 示例
1. **运行 BLASTn（不建库）**：
   ```bash
   python3 run_blastn.py -q /path/to/query.fa -o /path/to/output.txt -d /path/to/db/my_db -e 1e-5 -m 10 -t 4 --header
   ```

2. **构建数据库并运行 BLASTn**：
   ```bash
   python3 run_blastn.py -q /path/to/query.fa -o /path/to/output.txt -d /path/to/db/my_db -e 1e-5 -m 10 -t 4 --header --make_db /path/to/reference.fa
   ```

3. **过滤 percent_identity >= 97**：
   ```bash
   python3 run_blastn.py -q /path/to/query.fa -o /path/to/output.txt -d /path/to/db/my_db -e 1e-5 -m 10 -t 4 --header --min_identity 97
   ```

## 输出格式
- **数据库文件**（若使用 `--make_db`）：生成在 `-d` 指定的路径（如 `/path/to/db/my_db.nhr` 等）。
- **比对结果**（`-o` 指定）：包含表头（若启用 `--header`）和过滤后的记录（若启用 `--min_identity`）。示例：
  ```
  query_id        subject_id      percent_identity        alignment_length        mismatches      gap_opens       q.start q.end   s.start s.end   evalue  bit_score
  seq1            ref_seq1        99.737                  380                     1               0               1       380     682     1061    0.0     697
  seq1            ref_seq2        98.684                  380                     5               0               1       380     730     351     0.0     675
  ...
  ```

## 注意事项
- **环境配置**：确保 Conda 环境 `blast` 已安装 NCBI BLAST+，并包含 `blastn` 和 `makeblastdb`。
- **数据库重复**：若 `-d` 指定的数据库已存在，需删除旧文件（`rm /path/to/db/my_db.*`）或更改路径。
- **权限**：确保有写入权限（`-d` 和 `-o` 路径）。
- **表头依赖**：使用 `--min_identity` 必须启用 `--header`，以正确解析 `percent_identity` 列。
- **无效行**：如果输出文件中包含无法解析的 `percent_identity`（非数字），脚本会打印警告并跳过。
- **macOS 线程数**：建议根据 CPU 核心数设置 `-t`（查看核心数：`sysctl -n hw.ncpu`），例如 `-t 4`。

## 故障排查
- **环境错误**：若提示 `blastn` 或 `makeblastdb` 未找到，检查 Conda 环境：
  ```bash
  conda activate blast
  which blastn
  ```
  - macOS 上，若 Conda 未初始化：
    ```bash
    conda init zsh
    source ~/.zshrc
    ```
- **数据库错误**：若 `makeblastdb` 失败，确认 `--make_db` 指定的 FASTA 文件有效且路径正确。
- **过滤问题**：若表头丢失或过滤结果不正确，请检查输出文件（`cat output.txt`）并提供给开发者。
- **macOS 路径错误**：确认路径使用 macOS 格式（如 `/Users/username/...`），避免 Linux 路径（如 `/home/...`）。

## 贡献
欢迎提交 issue 或 pull request！请在 GitHub 仓库提出建议或报告问题.
