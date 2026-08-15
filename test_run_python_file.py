from functions.run_python_file import run_python_file


def main():
    result = run_python_file("calculator", "main.py")
    print(result)
    print()

    result = run_python_file("calculator", "main.py", ["3 + 5"])
    print(result)
    print()

    result = run_python_file("calculator", "tests.py")
    print(result)
    print()

    result = run_python_file("calculator", "../main.py")
    print(result)
    print()

    result = run_python_file("calculator", "nonexistent.py")
    print(result)
    print()

    result = run_python_file("calculator", "lorem.txt")
    print(result)
    print()


if __name__ == "__main__":
    main()