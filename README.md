# Duplicate-Detector

Made a duplicate detector in python as a project using the xx64 hashing library. This library can hash at an astonishing rate of 20 GB/s and performs well with small data and ensures as few collisions as possible.
Duplicate detector is highly customizable, allowing users to set how much data to hash of a file and where in the file to start hashing from. This allows the user to be able to control how likely it is for a
collisions to occur and the speed at which the program can hash and find duplicates.

It finds duplicates by first getting all the files that have the same size then hashes those files and associates paths with them.
At the end, the program outputs all found duplicates into a text file.

# Features Planned

- Allowing the user to delete files/folders directly from the program itself.
- Making a graphical user interface to allow the user to manipulate what to do with the duplicate files
