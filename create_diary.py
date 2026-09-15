# 当日の日付を参照して
# diaryフォルダ配下に日付フォルダとindex.mdを作成する
from datetime import date
from pathlib import Path
import subprocess
import shutil


def create_diary_page() -> Path:
	"""当日分の日記フォルダとindex.mdを作成する。

	Returns:
		作成または既存の日記ページへのパス。
	"""
	repository_root = Path(__file__).resolve().parent
	diary_directory = repository_root / "diary" / date.today().isoformat()
	diary_directory.mkdir(parents=True, exist_ok=True)

	index_file = diary_directory / "index.md"
	index_file.touch(exist_ok=True)
	folder_path = str(diary_directory)
	file_path = str(index_file)
	code = shutil.which("code.cmd")
	if code is None:
		raise FileNotFoundError("code.cmdが見つかりません")
	subprocess.Popen(
		[code, folder_path, file_path],
		creationflags=subprocess.CREATE_NO_WINDOW,
	)
	return index_file


def main() -> None:
	"""当日分の日記ページを作成して開く。"""
	create_diary_page()



if __name__ == "__main__":
	main()