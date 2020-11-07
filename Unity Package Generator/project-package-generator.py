import os
import sys
import argparse
import shutil
import datetime
import re

###### Utils #####
def sanitised_input(inputMsg, pattern, errorMsg, currentValue):
    #print(inputMsg)
    while True:
        ui = input(inputMsg)
        if not ui:
            ui = currentValue
        if re.match(pattern, ui):
            return ui
        else:
            print("Input type must be " + errorMsg)

def replace_in_file(filePath, beforeText, afterText):
    with open(filePath, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(beforeText, afterText)
    with open(filePath, 'w') as file:
        file.write(filedata)

###### End Utils #####


def createArgsParser():
    # create the top-level parser
    topParser = argparse.ArgumentParser()
    subparsers = topParser.add_subparsers()

    createParser = subparsers.add_parser('create', help='Command to create / initialize a new package project architecture.')
    createParser.add_argument('--package_identifier', type=str, help='Package identifier like com.ndy.package-name', default='com.yourcompany.yourpackage' , required='-i' not in sys.argv)
    createParser.add_argument('--root_namespace', type=str, help='Root namespace like NDY', default='' )
    createParser.add_argument('--display_name', type=str, help='Display name of this package.', default='Your Package')
    createParser.add_argument('--project_path', type=str, help='Path where you want to create your project.', default='./')
    createParser.add_argument('--author', type=str, help='Name of the author of this package.', default='')
    createParser.add_argument('-i', action='store_true', dest='interactive', help='Make the creation process interactive.', default=False)
    createParser.set_defaults(func=createCMD)

    return topParser

def createCMD(args):
    scriptDirectory = os.path.dirname(os.path.abspath(__file__))
    package_identifier = args.package_identifier
    display_name = args.display_name
    author = args.author
    root_namespace = args.root_namespace

    if (args.interactive):
        package_identifier = sanitised_input("Enter the package name (" + package_identifier + "): ", "^com\.[a-z0-9@]{1}[a-z0-9@\-_]*\.[a-z0-9@]{1}[a-z0-9@\-_]*$",
            "Please enter a valid package name like `com.yourcompany.yourpackage`.", package_identifier)
        display_name = sanitised_input("Enter the display name of your package (" + display_name + "): ", "\w*", "Please enter a valid display name like `Your Package`",
            display_name)
        author = sanitised_input("Enter the author name (" + args.author + "): ", "\w*", "Please enter a valid author name like `David Zamani-Kord`", args.author)

    strippedPackageIdentifier = package_identifier.replace("com.", "")
    splittedPackageIdentifier = strippedPackageIdentifier.split(".")
    cleanedPackageIdentifier = ""
    
    for i in range(len(splittedPackageIdentifier)):
        strSplit = splittedPackageIdentifier[i]
        cleanedPackageIdentifier += strSplit.capitalize()
        if (i != len(splittedPackageIdentifier) - 1):
            cleanedPackageIdentifier += "."
    
    createFolderStructure(scriptDirectory, args.project_path, package_identifier, cleanedPackageIdentifier)

    # Handle readme
    filePath = os.path.join(args.project_path, package_identifier, "README.md")
    replace_in_file(filePath, '[%PACKAGE_IDENTIFIER%]', package_identifier)
    replace_in_file(filePath, '[%DISPLAY_NAME%]', display_name)

    # Handle changelog
    today = datetime.date.today()  
    filePath = os.path.join(args.project_path, package_identifier, "CHANGELOG.md")
    replace_in_file(filePath, '[%CHANGELOG_DATE%]', str(today))

    # Handle license of package test project
    filePath = os.path.join(args.project_path, "LICENSE")
    replace_in_file(filePath, '[%AUTHOR%]', author)

    # Handle license of package
    filePath = os.path.join(args.project_path, package_identifier, "LICENSE")
    replace_in_file(filePath, '[%AUTHOR%]', author)

    # Handle package.json
    filePath = os.path.join(args.project_path, package_identifier, "package.json")
    replace_in_file(filePath, '[%PACKAGE_IDENTIFIER%]', package_identifier)
    replace_in_file(filePath, '[%DISPLAY_NAME%]', display_name)

    # Handle manifest.json
    filePath = os.path.join(args.project_path, "Packages", "manifest.json")
    replace_in_file(filePath, '[%PACKAGE_IDENTIFIER%]', package_identifier)
    
    # Handle asmdef
    filePath = os.path.join(args.project_path, package_identifier, "Runtime", cleanedPackageIdentifier + ".asmdef")
    replace_in_file(filePath, '[%CAPITALIZED_PACKAGE_IDENTIFIER%]', cleanedPackageIdentifier)
    replace_in_file(filePath, '[%ROOT_NAMESPACE%]', root_namespace)
    filePath = os.path.join(args.project_path, package_identifier, "Editor", cleanedPackageIdentifier + ".Editor.asmdef")
    replace_in_file(filePath, '[%CAPITALIZED_PACKAGE_IDENTIFIER%]', cleanedPackageIdentifier)
    replace_in_file(filePath, '[%ROOT_NAMESPACE%]', root_namespace)

def createFolderStructure(scriptDirectory, projectPath, packageIdentifier, cleanedPackageIdentifier):
    try:
        os.makedirs(os.path.join(projectPath, "Assets"), exist_ok=True)
        os.makedirs(os.path.join(projectPath, "ProjectSettings"), exist_ok=True)
        os.makedirs(os.path.join(projectPath, "Packages"), exist_ok=True)
        os.makedirs(os.path.join(projectPath, packageIdentifier, "Runtime"), exist_ok=True)
        os.makedirs(os.path.join(projectPath, packageIdentifier, "Editor"), exist_ok=True)
        os.makedirs(os.path.join(projectPath, packageIdentifier, "Documentation"), exist_ok=True)

        shutil.copy2(os.path.join(scriptDirectory, "Resources", "LICENSE.md"), os.path.join(projectPath, "LICENSE"))
        shutil.copy2(os.path.join(scriptDirectory, "Resources", "LICENSE.md"), os.path.join(projectPath, packageIdentifier, "LICENSE"))
        shutil.copy2(os.path.join(scriptDirectory, "Resources", "README.md"), os.path.join(projectPath, packageIdentifier, "README.md"))
        shutil.copy2(os.path.join(scriptDirectory, "Resources", "CHANGELOG.md"), os.path.join(projectPath, packageIdentifier, "CHANGELOG.md"))

        shutil.copy2(os.path.join(scriptDirectory, "Resources", "package.json"), os.path.join(projectPath, packageIdentifier, "package.json"))
        shutil.copy2(os.path.join(scriptDirectory, "Resources", "manifest.json"), os.path.join(projectPath, "Packages", "manifest.json"))
        
        shutil.copy2(os.path.join(scriptDirectory, "Resources", "manifest.json"), os.path.join(projectPath, "ProjectSettings", "ProjectVersion.txt"))

        shutil.copy2(os.path.join(scriptDirectory, "Resources", "Runtime.asmdef"), os.path.join(projectPath, packageIdentifier, "Runtime", cleanedPackageIdentifier + ".asmdef"))
        shutil.copy2(os.path.join(scriptDirectory, "Resources", "Editor.asmdef"), os.path.join(projectPath, packageIdentifier, "Editor", cleanedPackageIdentifier + ".Editor.asmdef"))

    except OSError as e:  
        print ("Creation of the directory %s failed" % e)
    else:  
        print ("Successfully created directories")  

def main():
    argsParser = createArgsParser()
    args = argsParser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
