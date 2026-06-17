import csv
import os
import sys

# 获取当前文件所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 计算 data 目录的绝对路径
data_path = os.path.abspath(os.path.join(current_dir, '../data/Chinese_surname.csv'))

with open(data_path, "r") as f:
    reader = csv.reader(f)
    # 可以用 set，但是为了方便维护，还是用 list
    CHINESE_SURNAME = [str(row[0]).upper() for row in reader]


def main():
    if len(sys.argv) > 1:
        new_surnames = sys.argv[1:]
        # print(new_surnames)
    else:
        # 如果不想输入，可以直接在这里修改
        new_surnames = ["xx", "xe"]
    surname_counter = 0
    for surname in new_surnames:
        if surname.upper() in CHINESE_SURNAME:
            print(f"Warning: {surname} is already in the list.")
        else:
            CHINESE_SURNAME.append(surname.upper())
            print(f"Adding {surname} to the list.")
            surname_counter += 1

    with open(data_path, "w") as f:
        writer = csv.writer(f)
        print(f"Writing {surname_counter} new surnames to Chinese_surname.csv")
        for surname in CHINESE_SURNAME:
            writer.writerow([surname])


if __name__ == '__main__':
    main()
