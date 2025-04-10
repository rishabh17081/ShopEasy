import java.io.File;
import java.io.IOException;

public class FileProcessor {

    // Method to check if a file exists
    public boolean checkIfFileExists(String filePath) {
        File file = new File(filePath);
        return file.exists();
    }

    // Method to create a new file
    public boolean createNewFile(String filePath) {
        File file = new File(filePath);
        try {
            return file.createNewFile();
        } catch (IOException e) {
            System.err.println("An error occurred while creating the file: " + e.getMessage());
            return false;
        }
    }

    // Method to delete a file
    public boolean deleteFile(String filePath) {
        File file = new File(filePath);
        return file.delete();
    }

    // Method to get the size of a file in bytes
    public long getFileSize(String filePath) {
        File file = new File(filePath);
        if (file.exists() && file.isFile()) {
            return file.length();
        } else {
            return -1; // Returns -1 if the file does not exist or is not a file
        }
    }

    // Main method to demonstrate the usage of the methods
    public static void main(String[] args) {
        FileProcessor fileProcessor = new FileProcessor();
        String filePath = "example.txt";

        // Check if the file exists
        System.out.println("File exists: " + fileProcessor.checkIfFileExists(filePath));

        // Create a new file
        if (fileProcessor.createNewFile(filePath)) {
            System.out.println("File created successfully.");
        } else {
            System.out.println("File creation failed.");
        }

        // Get the size of the file
        long fileSize = fileProcessor.getFileSize(filePath);
        if (fileSize != -1) {
            System.out.println("File size: " + fileSize + " bytes");
        } else {
            System.out.println("Unable to get file size.");
        }
        
         // Delete the file
        if (fileProcessor.deleteFile(filePath)) {
            System.out.println("File deleted successfully.");
        } else {
            System.out.println("File deletion failed.");
        }
    }
}