from functions.get_files_info import get_files_info


def main():
    result = get_files_info("calculator", ".")
    print("Result for current directory:")  # NEW: label before printing
    print(result)
    print()  # NEW: blank line for readability between results

    result = get_files_info("calculator", "pkg")
    print("Result for 'pkg' directory:")  
    print(result)
    print()  

    result = get_files_info("calculator", "/bin")
    print("Result for '/bin' directory:") 
    print(result)
    print()  

    result = get_files_info("calculator", "../")
    print("Result for '../' directory:")  
    print(result)
    print()  


if __name__ == "__main__":
    main()