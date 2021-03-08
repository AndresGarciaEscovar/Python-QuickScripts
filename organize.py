# Imports.
import os
import re
import csv
import numpy as np

def get_blocks_of_files(files_data, folders):
    """ Gets main folders with all the sub-folders and the rest of the branch,
        in blocks.

        :param file_data: The string with the file contents.
        :param folders: The root folders.

        :return An array with the strings that represent the root folders with
        the sub-folders.
    """

    # Check that the files data is a string and the folders is a list.
    if type(files_data) != type(" ") or type(folders) != type(["",""]):
        raise TypeError

    # Auxiliary variables.
    blocks = []

    for i, _ in enumerate(folders):

        # Auxiliary variables.
        block1 = ""

        # Get the name of the ith folder.
        str1 = "./" + folders[i] + ":"

        if i == len(folders) - 1:
            # If it is the last folder just split once.
            block1 = (str1 + files_data.split(str1)[1]).strip()

        else:
            # Get the ith folder and the next folder.
            str2 = "./" +  folders[i+1] + ":"

            block1 = files_data.split(str1)[1]
            block1 =  str1 + block1.split(str2)[0]

        # Delete the folders in the list.
        block1 = block1.split("\n")
        block2 = []
        for j, elem in enumerate(block1):
            if "." in elem:
                block2 += [elem.strip()]

        # Add the particular block to the block of blocks.
        blocks += ["\n".join(block2)]

    #  Return the complete list of blocks.
    return blocks

def get_file_data(file_name):
    """ Gets the data loaded from the file.

        :param file_name: The name of the file from the data is to be extracted.

        :return The data that contains the tree structure of the folders and
        files.
    """

    # Check that the parameter is a string.
    if(type(file_name) !=  str):
        raise TypeError()

    # Get the files.
    with open(file_name, 'r') as fl:
        reader = fl.readlines()
        lst = " ".join(reader)
        return lst

def get_formatted_table(header, table):
    """ Gets the table properly formatted for export, i.e., an nx1 matrix.

        :param header: The header of the table.
        ::param table: A pre-formatted table that contains ALL the required
        information. Just needs to be properly formatted for export.

        :return A properly formatted table to export as a csv file.
    """

    # Auxiliary variables.
    tmpHeader = (header + [""]) * len(table)
    tmpTable = [x for x in table]

    # Get the maximum length of each entry.
    maxLength = [len(x) for x in tmpTable]
    maxTblLength = max(maxLength)

    # This for each table element.
    for i, _ in enumerate(table):

        # Append a space at the end of each row.
        for j, _ in enumerate(table[i]):
            tmpTable[i][j] += [""]

        # Append the number of rows such that the entries of the table have the same number of rows.
        for j in range(maxTblLength - maxLength[i]):
            tmpTable[i] += [["" for x in range(len(table[i][0]))]]

        # Append all the rows of the ith entry to each row of the zeroth entry.
        if i > 0:
            for j, _ in enumerate(tmpTable[0]):
                tmpTable[0][j] += tmpTable[i][j]

    # Remove all the entries except the first one.
    for i in range(len(tmpTable) - 1):
        tmpTable.pop(1)

    # Add the header at the beginning of the table.
    tmpTable[0] = [tmpHeader ] + tmpTable[0]

    # Check all the rows have the same length.
    checkNumber = len(tmpTable[0][0])
    for i in tmpTable[0]:
        if checkNumber != len(i):
            raise ValueError("All rows must have the same length.")

    # Return the final table.
    return  tmpTable

def get_hoomd_in_file(table, filter_true):
    """ Gets the table with the final entry filled, i.e., if the file is a
        python file, it opens it and searchs for hoomd. If hoomd is installed,
        it fills the last entry of the table with true, otherwise false.

        :param table: A pre-formatted table that contains ALL the needed columns
        to fill in the reamining required information.

        :return A properly formatted table with the information about the
        existence of hoomd.
    """

    # Check  that a table is being passed.
    if type(table) != type(["" , ""]):
        raise TypeError

    # Create a temporary variable.
    tmpTable1 = []
    tmpTable0 = [x for x in table]

    # Do it for everythin block.
    for i, block in enumerate(table):

        # Do it for every element in the block.
        for j, elem in enumerate(block):

            # Get the file path.
            file_path = [x for x in elem if x != ""]
            file_path = "." + os.sep + (os.sep).join(file_path)

            # Open only python files.
            if file_path[-3:] == ".py" or file_path[-4:] == ".txt" :
                # Try to open the file.
                with open(file_path, 'r') as fl:

                    # Read all the lines and set it as a string.
                    reader = fl.readlines()
                    reader = "".join(reader)

                    # Try find hoomd.
                    if re.search("hoomd", reader, re.IGNORECASE):
                        tmpTable0[i][j][-1] = "True"
                    else:
                        tmpTable0[i][j][-1] = "False"
            else:
                # Other files do not matter.
                tmpTable0[i][j][-1] = "False"

    # Filter the files.
    if filter_true:

        # Get the indexes.
        indexes = []

        # Look at each block.
        for i, block in enumerate(tmpTable0):

            # Do it for every element in the block.
            for j, elem in enumerate(block):

                # Only filter the entries that have hoomd.
                if tmpTable0[i][j][-1] == "True":
                    indexes += [[i,j]]

        # Only do this if the index exists.
        if len(indexes) > 0 :
            indexList = list(set(np.array(indexes)[:,0]))
            tmpTable1 = [ [] for x in indexList]

            # Go through the first index list.
            for i, elem0 in enumerate(indexList):

                # Go throught the list.
                for j, elem1 in enumerate(indexes):
                    # Only add indexes that are in the same block.
                    if indexes[j][0] == elem0:
                        tmpTable1[i] += [ tmpTable0[elem1[0]][elem1[1]]]

            # Replace the table.
            tmpTable0 = tmpTable1

    # Return the final table.
    return  tmpTable0

def get_main_folders(file_data):
    """ Get the folders stored in the root of the document.

        :param: file_data: The string with the file contents.

        :return A list of the folders in the root directory.
    """

    # Check that the file_data is a string.
    if(type(file_data) != type(" ")):
        raise TypeError()

    # Format the folders in an array.
    main_folders = file_data.split("./")[0].strip()
    main_folders = main_folders.split("\n")
    main_folders.pop(0)
    main_folders = [x.strip() for x in main_folders]

    # Return the folders.
    return  main_folders

def get_maximum_depth(blocks):
    """ Get the depth of the deepest branch.

        :param: blocks: The blocks of all the folders with their sub-folders.

        :return The maximum depth of the maximum depths of each branch.
    """

    # Check that the blocks data is a list of strings.
    if type(blocks) != type(["",""]):
        raise TypeError

    # Set the maximum depth of the blocks to at least 1.
    maxArray = [1 for i in blocks]

    # Obtain the depth for each branch.
    for i, block in enumerate(blocks):

        # Get the branches for each block and only get the sub-folders
        folders = block.split("\n")
        folders = [x[2:] for x in folders if "./" in x]

        # Use the path separator to calculate the maximum depth.
        for j, file_name in enumerate(folders):
            maxArray[i] = max([maxArray[i], len(file_name.split("/"))])

    # Return the maximum depth of the tree from its root.
    return  max(maxArray)

def get_table(header, blocks):
    """ Gets the partial table to be displayed in the file.

        :param header: The header of the table.
        :param blocks: The blocks of folders and files.

        :return Gets a pre-formatted table with all the needed entries, some of
        which need to be filled.
    """

    # Check that the header is a list of strings and also the blocks.
    if type(header) != type([" "]) or type(blocks) != type([" "," "]):
        raise TypeError

    # Create an empty array for a table.
    table_form = []

    # Format each block.
    for i, block in enumerate(blocks):

        # Create a list of empty place-holders to accomodate the folders and files.
        placeholders = ["" for x in header]

        # Get the file and folder entries for each block.
        tmp = ""
        entryLst = []
        entries = block.split("\n")
        for j, entry in enumerate(entries):

            if "./" in entry:
                # Get the folders and the sub-folders.
                tmp = entry[2:].split("/")
                for k in range(len(tmp)):
                    if ":" in tmp[k]:
                        placeholders[k] = tmp[k][:-1].strip()
                    else:
                        placeholders[k] = tmp[k].strip()
            else:
                # Get the file in the folder.
                placeholders[-2] = entry

            if placeholders[-2] != "":
                # Add the entry if there is a file.
                tableEntry = [x for x in placeholders]
                entryLst += [tableEntry]

            # Reset the placeholder
            placeholders = ["" for x in header]
            for k in range(len(tmp)):
                if ":" in tmp[k]:
                    placeholders[k] = tmp[k][:-1].strip()
                else:
                    placeholders[k] = tmp[k].strip()

        # Store the result in the table.
        table_form +=[entryLst]

    # Return the partial form of the table to be printed.
    return  table_form

def get_table_header(max_depth):
    """ Gets the table header for the data frame.

        :param max_depth: The maximum depth of the branches.

        return The table header.
    """

    # Check that max_depth is a positive integer greater than zero.
    if type(max_depth) != type(int(0)) or max_depth <= 0:
        raise TypeError

    # Set the header for the files.
    header = ["Folder"] + [("Sub-"*i) + "Folder" for i in range(1,max_depth) ] + ["File name", "In Hoomd"]

    # Return the header to be used for the csv file.
    return  header

def save_table(table, save_file_name =  "."+ os.sep + "organizedFiles.csv"):
    """ Saves the table to the given save_file_name.

        :param table: The table to be saved. Must have only one entry with
        several rows of the same length.
        :param save_file_name: The FULL name, with the desired extension, and
        full path of the file where the table is to be saved. The default path
        will be ./organizedFiles.csv.
    """

    # Save the file with csv writer.
    with open(save_file_name, "w") as fl:
        writer = csv.writer(fl)
        writer.writerows(table[0])

def process_files(file_name, save_file_name, filter_true):

    # Obtain the file information.
    files_data = get_file_data(file_name)

    # Extract main folders from the string.
    folders = get_main_folders(files_data)

    # Get the blocks of files per main folder.
    blocks = get_blocks_of_files(files_data, folders)

    # Calculate the depth of the deepest branch.
    max_depth = get_maximum_depth(blocks)

    # Get the header for the table.
    header = get_table_header(max_depth)

    # Pre-format the table to be exported.
    table = get_table(header, blocks)

    # Get the existence of hoomd in the package.
    table = get_hoomd_in_file(table, filter_true)

    # Final table formatting.
    table = get_formatted_table(header, table)

    # Save the table in the desired path.
    save_table(table, save_file_name)

if __name__ == "__main__":
    filter_true = True
    file_name = "filesAndDirectories.txt"
    save_file_name = "filesAndDirectories.csv"
    process_files(file_name, save_file_name, filter_true)
