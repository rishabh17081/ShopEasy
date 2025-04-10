import re
import os
import glob
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from langchain_text_splitters import TextSplitter
from langchain_core.documents import Document


@dataclass
class JavaCodeSegment:
    """Represents a semantic segment of Java code with enhanced context."""
    text: str
    segment_type: str  # package, import, class, method, field, method_part
    name: str
    parent_class: Optional[str] = None
    filename: Optional[str] = None
    package_name: Optional[str] = None
    javadoc: Optional[str] = None
    signature: Optional[str] = None
    references: List[str] = field(default_factory=list)
    part_number: Optional[int] = None
    total_parts: Optional[int] = None

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get enhanced metadata for this segment with improved context."""
        meta = {
            "type": self.segment_type,
            "name": self.name,
        }
        
        # Add hierarchical and contextual information
        if self.parent_class:
            meta["class"] = self.parent_class
        
        if self.filename:
            meta["filename"] = self.filename
            
        if self.package_name:
            meta["package"] = self.package_name
            # Create fully qualified name for better context
            if self.parent_class:
                meta["full_qualified_name"] = f"{self.package_name}.{self.parent_class}.{self.name}"
            elif self.segment_type == "class":
                meta["full_qualified_name"] = f"{self.package_name}.{self.name}"
                
        # Add a context path for hierarchical reference
        context_parts = []
        if self.filename:
            context_parts.append(self.filename)
        if self.package_name:
            context_parts.append(self.package_name)
        if self.parent_class:
            context_parts.append(self.parent_class)
        context_parts.append(self.name)
        meta["context_path"] = "/".join(context_parts)
        
        # Add method signature if available
        if self.signature:
            meta["signature"] = self.signature
            
        # Add references to other methods/classes
        if self.references:
            meta["references"] = self.references
            
        # Add part information for split methods
        if self.part_number is not None:
            meta["part_number"] = self.part_number
            meta["total_parts"] = self.total_parts
            
        # Include javadoc summary if available
        if self.javadoc:
            # Extract first sentence or line as summary
            first_line = self.javadoc.split('.')[0].strip()
            if len(first_line) > 100:
                first_line = first_line[:97] + "..."
            meta["javadoc_summary"] = first_line
            
        return meta


class EnhancedJavaSemanticParser:
    """
    An enhanced semantic Java code parser with improved context preservation
    for better RAG retrieval.
    """

    # Patterns for Java code structure
    CLASS_PATTERN = re.compile(
        r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w,\s]+)?\s*\{',
        re.MULTILINE
    )
    
    CLASS_SIGNATURE_PATTERN = re.compile(
        r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?\s*\{',
        re.MULTILINE
    )

    METHOD_PATTERN = re.compile(
        r'(?:public|private|protected)?\s*(?:static|final|abstract|synchronized)?\s*(?:<[^>]+>)?\s*(?:[\w<>\[\]]+)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{',
        re.MULTILINE
    )
    
    METHOD_SIGNATURE_PATTERN = re.compile(
        r'(?:public|private|protected)?\s*(?:static|final|abstract|synchronized)?\s*(?:<[^>]+>)?\s*([\w<>\[\]]+)\s+(\w+)\s*\(([^)]*)\)(?:\s*throws\s+([\w,\s]+))?',
        re.MULTILINE
    )

    FIELD_PATTERN = re.compile(
        r'(?:public|private|protected)?\s*(?:static|final|volatile|transient)?\s*(?:[\w<>\[\]]+)\s+(\w+)(?:\s*=\s*[^;]+)?;',
        re.MULTILINE
    )

    IMPORT_PATTERN = re.compile(
        r'import\s+(?:static)?\s*([\w.]+)\s*;',
        re.MULTILINE
    )

    PACKAGE_PATTERN = re.compile(
        r'package\s+([\w.]+)\s*;',
        re.MULTILINE
    )
    
    JAVADOC_PATTERN = re.compile(
        r'/\*\*\s*(.*?)\s*\*/', 
        re.DOTALL
    )
    
    METHOD_CALL_PATTERN = re.compile(
        r'(?<!\.)(\w+)\s*\([^)]*\)',
        re.MULTILINE
    )
    
    OBJECT_METHOD_CALL_PATTERN = re.compile(
        r'(\w+)\.(\w+)\s*\([^)]*\)',
        re.MULTILINE
    )

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the parser with configurable chunk size.
        
        Args:
            chunk_size: Maximum size for method chunks
            chunk_overlap: Overlap size for method chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def read_java_file(self, file_path: str) -> str:
        """
        Read a Java file and return its content.

        Args:
            file_path: Path to the Java file

        Returns:
            Content of the Java file as a string
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def parse_java_file(self, file_path: str) -> Document:
        """
        Parse a Java file and return a LangChain Document with its content.

        Args:
            file_path: Path to the Java file

        Returns:
            Document containing the parsed code
        """
        content = self.read_java_file(file_path)

        metadata = {
            "filename": os.path.basename(file_path),
            "filepath": file_path,
            "type": "java_file",
            "is_java": True,
            "relative_path": os.path.basename(file_path)
        }

        return Document(page_content=content, metadata=metadata)

    def find_matching_brace(self, text: str, start_idx: int) -> int:
        """
        Find the matching closing brace given the opening brace position.

        Args:
            text: Text to search in
            start_idx: Index after the opening brace

        Returns:
            Index of the matching closing brace
        """
        brace_count = 1
        end = start_idx

        while brace_count > 0 and end < len(text):
            if text[end] == '{':
                brace_count += 1
            elif text[end] == '}':
                brace_count -= 1
            end += 1

        return end
        
    def extract_javadoc(self, content: str, start_pos: int) -> Optional[str]:
        """
        Extract Javadoc comment before a given position.
        
        Args:
            content: Java code content
            start_pos: Position where the code element starts
            
        Returns:
            Extracted Javadoc comment or None if not found
        """
        # Search backwards from the position (limited to reasonable javadoc size)
        search_limit = max(0, start_pos - 2000)
        content_before = content[search_limit:start_pos]
        match = list(self.JAVADOC_PATTERN.finditer(content_before))
        if match:
            # Return the last match (closest to the code element)
            javadoc = match[-1].group(1).strip()
            # Clean up javadoc by removing * at line beginnings
            javadoc = re.sub(r'\n\s*\*\s*', '\n', javadoc)
            return javadoc
        return None

    def extract_package(self, content: str, filename: str) -> Optional[JavaCodeSegment]:
        """
        Extract package information from Java code.

        Args:
            content: Java code content
            filename: Name of the source file

        Returns:
            A JavaCodeSegment for the package or None if not found
        """
        match = self.PACKAGE_PATTERN.search(content)
        if match:
            package_name = match.group(1)
            return JavaCodeSegment(
                text=match.group(),
                segment_type="package",
                name=package_name,
                filename=filename,
                package_name=package_name
            )
        return None

    def extract_imports(self, content: str, filename: str, package_name: Optional[str] = None) -> Optional[JavaCodeSegment]:
        """
        Extract import statements from Java code.

        Args:
            content: Java code content
            filename: Name of the source file
            package_name: Name of the package (if available)

        Returns:
            A JavaCodeSegment for the imports or None if not found
        """
        imports = []
        for match in self.IMPORT_PATTERN.finditer(content):
            imports.append(match.group())

        if imports:
            return JavaCodeSegment(
                text="\n".join(imports),
                segment_type="imports",
                name="imports",
                filename=filename,
                package_name=package_name
            )
        return None
        
    def extract_method_signature(self, method_match) -> Optional[str]:
        """
        Extract a clean method signature with return type and parameters.
        
        Args:
            method_match: Regex match for the method
            
        Returns:
            Method signature string
        """
        full_match = method_match.group(0)
        signature_match = self.METHOD_SIGNATURE_PATTERN.search(full_match)
        if signature_match:
            return_type = signature_match.group(1)
            method_name = signature_match.group(2)
            params = signature_match.group(3)
            throws = signature_match.group(4)
            
            signature = f"{return_type} {method_name}({params})"
            if throws:
                signature += f" throws {throws}"
            return signature
        return None
        
    def extract_method_calls(self, method_content: str) -> Set[str]:
        """
        Extract method calls from a method body.
        
        Args:
            method_content: Method body content
            
        Returns:
            Set of method names called
        """
        # Extract direct method calls (not preceded by a dot)
        direct_calls = set(match.group(1) for match in self.METHOD_CALL_PATTERN.finditer(method_content))
        
        # Also extract method calls on objects
        object_calls = set(match.group(2) for match in self.OBJECT_METHOD_CALL_PATTERN.finditer(method_content))
        
        # Combine both types of calls
        all_calls = direct_calls.union(object_calls)
        
        # Filter out common Java methods that aren't likely to be user-defined
        common_methods = {"equals", "toString", "hashCode", "get", "set", "add", "remove", 
                         "size", "length", "charAt", "substring", "indexOf", "println", 
                         "print", "format", "append", "close", "value", "next"}
        
        return {call for call in all_calls if call not in common_methods}

    def extract_class_info(self, content: str, match) -> Tuple[str, Optional[str]]:
        """
        Extract class name and signature.
        
        Args:
            content: Java code content
            match: Regex match for the class
            
        Returns:
            Tuple of (class_name, class_signature)
        """
        class_name = match.group(1)
        signature_match = self.CLASS_SIGNATURE_PATTERN.search(content[match.start():match.end() + 100])
        
        if signature_match:
            extends = signature_match.group(2)
            implements = signature_match.group(3)
            
            signature = f"class {class_name}"
            if extends:
                signature += f" extends {extends}"
            if implements:
                signature += f" implements {implements}"
                
            return class_name, signature
        
        return class_name, None

    def split_method_into_chunks(
        self, 
        method_content: str, 
        method_name: str,
        signature: str,
        javadoc: Optional[str],
        parent_class: str, 
        package_name: Optional[str],
        filename: str
    ) -> List[JavaCodeSegment]:
        """
        Split large methods into overlapping chunks while preserving context.
        
        Args:
            method_content: The method content
            method_name: Name of the method
            signature: Method signature
            javadoc: Method Javadoc comment
            parent_class: Name of the containing class
            package_name: Name of the package
            filename: Name of the source file
            
        Returns:
            List of method chunk segments
        """
        # If method is small enough, return as single chunk
        if len(method_content) <= self.chunk_size:
            # Extract method calls for references
            method_calls = self.extract_method_calls(method_content)
            
            return [JavaCodeSegment(
                text=method_content,
                segment_type="method",
                name=method_name,
                parent_class=parent_class,
                package_name=package_name,
                filename=filename,
                signature=signature,
                javadoc=javadoc,
                references=list(method_calls),
                part_number=1,
                total_parts=1
            )]
        
        # Otherwise, split into overlapping chunks
        chunks = []
        
        # Always include header (signature and javadoc) with each chunk
        header = f"// From class: {parent_class}\n"
        if signature:
            header += f"// Signature: {signature}\n"
        if javadoc:
            # Add a shortened javadoc summary
            javadoc_summary = javadoc.split("\n")[0]
            if len(javadoc_summary) > 100:
                javadoc_summary = javadoc_summary[:97] + "..."
            header += f"// Javadoc: {javadoc_summary}\n"
            
        # Calculate effective chunk size (accounting for header)
        effective_chunk_size = self.chunk_size - len(header)
        
        # Create overlapping chunks
        total_chunks = (len(method_content) - 1) // (effective_chunk_size - self.chunk_overlap) + 1
        
        for i in range(total_chunks):
            start = i * (effective_chunk_size - self.chunk_overlap)
            end = min(start + effective_chunk_size, len(method_content))
            
            # Extract the chunk and add the context header
            chunk = method_content[start:end]
            chunk_with_context = f"{header}// Part {i+1} of {total_chunks}\n{chunk}"
            
            # Extract method calls for references (for this chunk only)
            method_calls = self.extract_method_calls(chunk)
            
            chunks.append(JavaCodeSegment(
                text=chunk_with_context,
                segment_type="method_part" if total_chunks > 1 else "method",
                name=method_name,
                parent_class=parent_class,
                package_name=package_name,
                filename=filename,
                signature=signature,
                javadoc=javadoc,
                references=list(method_calls),
                part_number=i + 1,
                total_parts=total_chunks
            ))
        
        return chunks

    def extract_methods(
        self, 
        class_body: str, 
        class_name: str, 
        class_signature: str,
        package_name: Optional[str], 
        filename: str,
        full_content: str,
        class_start: int
    ) -> List[JavaCodeSegment]:
        """
        Extract methods from a class body with enhanced context.
        Fields are intentionally excluded to focus on method-based chunking.

        Args:
            class_body: The body of the class
            class_name: Name of the containing class
            class_signature: Signature of the class
            package_name: Package name
            filename: Name of the source file
            full_content: Full file content (for javadoc extraction)
            class_start: Start position of the class in the full content

        Returns:
            List of JavaCodeSegments for methods with enhanced context
        """
        segments = []

        # Extract methods with enhanced context
        for match in self.METHOD_PATTERN.finditer(class_body):
            method_name = match.group(1)
            start = match.start()
            
            # Extract javadoc for this method
            absolute_method_pos = class_start + match.start()
            javadoc = self.extract_javadoc(full_content, absolute_method_pos)
            
            # Extract method signature
            signature = self.extract_method_signature(match)
            
            # Find method body
            method_body_start = class_body.find('{', start)
            if method_body_start != -1:
                end = self.find_matching_brace(class_body, method_body_start + 1)
                
                if end > start:
                    method_content = class_body[start:end]
                    
                    # Split method into chunks if needed
                    method_chunks = self.split_method_into_chunks(
                        method_content=method_content,
                        method_name=method_name,
                        signature=signature,
                        javadoc=javadoc,
                        parent_class=class_name,
                        package_name=package_name,
                        filename=filename
                    )
                    
                    segments.extend(method_chunks)

        # Note: Field extraction is intentionally excluded to focus on method-based chunking

        return segments

    def semantic_chunking(self, document: Document) -> List[Document]:
        """
        Split a Java document into semantic chunks with enhanced context,
        focusing only on methods and excluding fields.

        Args:
            document: The Java document to split

        Returns:
            List of documents representing semantic chunks with enhanced context
        """
        filepath = document.metadata.get("filepath", "Unknown path")
        filename = document.metadata.get("filename", "Unknown file")
        print(f"\nSemantically chunking Java file: {filepath}")

        segments = []
        content = document.page_content
        package_name = None

        # Extract package info
        package_segment = self.extract_package(content, filename)
        if package_segment:
            segments.append(package_segment)
            package_name = package_segment.name
            print(f"  - Found package declaration: {package_segment.name}")
        else:
            print(f"  - No package declaration found")

        # Extract imports with package context
        imports_segment = self.extract_imports(content, filename, package_name)
        if imports_segment:
            segments.append(imports_segment)
            # Count number of imports by counting newlines
            import_count = imports_segment.text.count('\n') + 1
            print(f"  - Found {import_count} import statements")
        else:
            print(f"  - No import statements found")

        class_count = 0
        method_count = 0
        method_part_count = 0

        # Extract classes with their content and enhanced context
        for match in self.CLASS_PATTERN.finditer(content):
            # Get class name and signature
            class_name, class_signature = self.extract_class_info(content, match)
            start = match.start()
            end = self.find_matching_brace(content, match.end())

            if end > start:
                class_content = content[start:end]
                class_body = content[match.end():end - 1]
                
                # Extract javadoc for this class
                javadoc = self.extract_javadoc(content, start)

                # Add semantic markers for better embedding
                enhanced_class = f"[CLASS_START]\n"
                if class_signature:
                    enhanced_class += f"// Signature: {class_signature}\n"
                if javadoc:
                    enhanced_class += f"// Javadoc: {javadoc}\n"
                enhanced_class += f"{class_content}\n[CLASS_END]"

                segments.append(JavaCodeSegment(
                    text=enhanced_class,
                    segment_type="class",
                    name=class_name,
                    package_name=package_name,
                    filename=filename,
                    signature=class_signature,
                    javadoc=javadoc
                ))
                class_count += 1

                # Focus only on methods - fields are intentionally excluded
                method_segments = self.extract_methods(
                    class_body, 
                    class_name, 
                    class_signature,
                    package_name, 
                    filename,
                    content,
                    start + match.end()
                )

                # Count different segment types
                for segment in method_segments:
                    if segment.segment_type == "method":
                        method_count += 1
                    elif segment.segment_type == "method_part":
                        method_part_count += 1

                segments.extend(method_segments)

        print(f"  - Found {class_count} classes")
        print(f"  - Found {method_count} methods")
        print(f"  - Found {method_part_count} method parts (from large methods)")
        print(f"  - Created {len(segments)} total chunks")

        # Convert segments to LangChain Documents with enhanced metadata
        return [
            Document(
                page_content=segment.text,
                metadata=segment.metadata
            ) for segment in segments
        ]


class EnhancedJavaCodeSplitter(TextSplitter):
    """
    A LangChain text splitter that splits Java code semantically with improved
    context preservation for better RAG retrieval.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the splitter with enhanced semantic parser.
        
        Args:
            chunk_size: Maximum size for method chunks
            chunk_overlap: Overlap size for method chunks
        """
        self.parser = EnhancedJavaSemanticParser(chunk_size, chunk_overlap)
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def split_text(self, text: str) -> List[str]:
        """
        Split text semantically. This is a required method for TextSplitter.

        Note: In practice, we'll use split_documents instead of this method.

        Args:
            text: The text to split

        Returns:
            List of text chunks
        """
        # This method is required by TextSplitter but we'll use split_documents instead
        return [text]

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into semantic chunks with enhanced context.

        Args:
            documents: List of documents to split

        Returns:
            List of semantically split documents with enhanced context
        """
        print(f"\nStarting enhanced semantic splitting of {len(documents)} Java documents")

        result = []
        for i, doc in enumerate(documents):
            print(f"\nProcessing document {i + 1}/{len(documents)}: {doc.metadata.get('filename', 'Unknown')}")
            chunks = self.parser.semantic_chunking(doc)
            result.extend(chunks)
            print(f"  → Created {len(chunks)} chunks")

        print(f"\nCompleted enhanced semantic splitting. Total chunks created: {len(result)}")
        return result


class EnhancedJavaProjectParser:
    """
    Enhanced parser for handling entire Java projects with improved context preservation.
    """

    # Extensions to be processed as Java files
    JAVA_EXTENSIONS = {'.java'}

    # Common text-based file extensions that can be loaded as documents without special parsing
    TEXT_EXTENSIONS = {
        '.txt', '.md', '.properties', '.xml', '.json', '.yaml', '.yml',
        '.gradle', '.html', '.css', '.js', '.ts', '.csv'
    }

    # Extensions to skip (binary or irrelevant files)
    SKIP_EXTENSIONS = {
        '.class', '.jar', '.war', '.ear', '.zip', '.tar', '.gz', '.jpg',
        '.jpeg', '.png', '.gif', '.bmp', '.ico', '.pdf', '.exe', '.dll',
        '.so', '.o', '.obj', '.pyc', '.pyo', '.pyd'
    }

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the enhanced project parser.
        
        Args:
            chunk_size: Maximum size for method chunks
            chunk_overlap: Overlap size for method chunks
        """
        self.java_parser = EnhancedJavaSemanticParser(chunk_size, chunk_overlap)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def is_java_file(self, file_path: str) -> bool:
        """Check if a file is a Java file based on its extension."""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.JAVA_EXTENSIONS

    def is_text_file(self, file_path: str) -> bool:
        """Check if a file is a text-based file that can be processed."""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.TEXT_EXTENSIONS

    def should_skip_file(self, file_path: str) -> bool:
        """Check if a file should be skipped (binary or irrelevant)."""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.SKIP_EXTENSIONS

    def _guess_file_type(self, file_path: str) -> str:
        """Try to determine the file type for metadata."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext in self.JAVA_EXTENSIONS:
            return "java"
        elif ext == '.xml':
            return "xml"
        elif ext == '.properties':
            return "properties"
        elif ext in {'.json'}:
            return "json"
        elif ext in {'.yaml', '.yml'}:
            return "yaml"
        elif ext in {'.md', '.markdown'}:
            return "markdown"
        elif ext == '.gradle':
            return "gradle"
        elif ext == '.html':
            return "html"
        elif ext == '.css':
            return "css"
        elif ext in {'.js', '.ts'}:
            return "script"
        elif ext == '.csv':
            return "data"
        else:
            return "text"

    def read_text_file(self, file_path: str) -> Document:
        """
        Read a non-Java text file and return it as a Document with enhanced metadata.

        Args:
            file_path: Path to the text file

        Returns:
            Document containing the file content with enhanced metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            file_type = self._guess_file_type(file_path)
            filename = os.path.basename(file_path)
            
            # Extract directory structure for better context
            dir_path = os.path.dirname(file_path)
            rel_path = os.path.relpath(file_path, os.path.dirname(dir_path)) if dir_path else filename
            
            # Try to infer package from directory structure for better context
            if file_type == "java":
                package_path = os.path.dirname(rel_path).replace(os.path.sep, '.')
                if package_path:
                    inferred_package = package_path
                else:
                    inferred_package = None
            else:
                inferred_package = None

            metadata = {
                "filename": filename,
                "filepath": file_path,
                "type": file_type,
                "relative_path": rel_path,
                "is_java": False,
                "context_path": rel_path  # Add context path for better retrieval
            }
            
            if inferred_package:
                metadata["inferred_package"] = inferred_package

            return Document(page_content=content, metadata=metadata)
        except UnicodeDecodeError:
            # If we can't read as UTF-8, it's likely a binary file
            # Return a placeholder document
            metadata = {
                "filename": os.path.basename(file_path),
                "filepath": file_path,
                "type": "binary",
                "relative_path": os.path.basename(file_path),
                "is_java": False,
                "error": "Could not decode as text"
            }
            return Document(page_content="[Binary content not displayed]", metadata=metadata)

    def parse_directory(self, directory_path: str, recursive: bool = True) -> List[Document]:
        """
        Parse all files in a directory with enhanced context.

        Args:
            directory_path: Path to the directory to parse
            recursive: Whether to recursively process subdirectories

        Returns:
            List of Documents from all processable files with enhanced context
        """
        all_documents = []

        print(f"\n{'=' * 80}")
        print(f"STARTING ENHANCED DIRECTORY SCAN: {directory_path}")
        print(f"Recursive mode: {recursive}")
        print(f"Using chunk size: {self.chunk_size}, overlap: {self.chunk_overlap}")
        print(f"{'=' * 80}")

        # Get all files in the directory (and subdirectories if recursive)
        if recursive:
            pattern = os.path.join(directory_path, '**', '*')
            files = glob.glob(pattern, recursive=True)
        else:
            pattern = os.path.join(directory_path, '*')
            files = glob.glob(pattern)

        # Filter out directories
        files = [f for f in files if os.path.isfile(f)]

        print(f"Found {len(files)} total files in directory")

        # Count file types for reporting
        java_files = 0
        text_files = 0
        skipped_files = 0
        error_files = 0

        # Process each file
        for file_path in files:
            if self.should_skip_file(file_path):
                print(f"SKIPPING (binary/irrelevant): {file_path}")
                skipped_files += 1
                continue

            if self.is_java_file(file_path):
                # Parse Java file and add resulting document
                try:
                    print(f"PROCESSING JAVA: {file_path}")
                    java_doc = self.java_parser.parse_java_file(file_path)
                    all_documents.append(java_doc)
                    java_files += 1
                except Exception as e:
                    print(f"ERROR parsing Java file {file_path}: {str(e)}")
                    error_files += 1
            elif self.is_text_file(file_path) or not self.should_skip_file(file_path):
                # Try to process as a text file
                try:
                    print(f"PROCESSING TEXT: {file_path}")
                    doc = self.read_text_file(file_path)
                    all_documents.append(doc)
                    text_files += 1
                except Exception as e:
                    print(f"ERROR processing file {file_path}: {str(e)}")
                    error_files += 1

        print(f"\n{'=' * 80}")
        print(f"DIRECTORY SCAN COMPLETE: {directory_path}")
        print(f"Java files processed: {java_files}")
        print(f"Text files processed: {text_files}")
        print(f"Files skipped: {skipped_files}")
        print(f"Files with errors: {error_files}")
        print(f"Total documents created: {len(all_documents)}")
        print(f"{'=' * 80}\n")

        return all_documents

    def process_project(self, directory_path: str, recursive: bool = True) -> List[Document]:
        """
        Process an entire Java project directory and return semantic chunks with enhanced context.

        Args:
            directory_path: Path to the project directory
            recursive: Whether to recursively process subdirectories

        Returns:
            List of semantic document chunks with enhanced context
        """
        print(f"\n{'#' * 80}")
        print(f"STARTING ENHANCED PROJECT PROCESSING: {directory_path}")
        print(f"Using chunk size: {self.chunk_size}, overlap: {self.chunk_overlap}")
        print(f"{'#' * 80}\n")

        documents = self.parse_directory(directory_path, recursive)

        print(f"\n{'#' * 80}")
        print(f"ENHANCED SEMANTIC CHUNKING PHASE")
        print(f"{'#' * 80}")

        # Parse Java documents into semantic chunks
        splitter = EnhancedJavaCodeSplitter(self.chunk_size, self.chunk_overlap)
        java_docs = [doc for doc in documents if doc.metadata.get("is_java", False) or
                     self.is_java_file(doc.metadata.get("filepath", ""))]

        non_java_docs = [doc for doc in documents if not (doc.metadata.get("is_java", False) or
                                                          self.is_java_file(doc.metadata.get("filepath", "")))]

        print(f"Found {len(java_docs)} Java documents to semantically chunk")
        print(f"Found {len(non_java_docs)} non-Java documents to preserve as-is")

        # Apply semantic splitting to Java documents
        if java_docs:
            print("Starting enhanced semantic chunking of Java documents...")
            split_java_docs = splitter.split_documents(java_docs)
            print(f"Created {len(split_java_docs)} semantic chunks from {len(java_docs)} Java files")

            # Print some statistics about chunk types
            chunk_types = {}
            for doc in split_java_docs:
                chunk_type = doc.metadata.get("type", "unknown")
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1

            print("\nChunk type distribution:")
            for chunk_type, count in sorted(chunk_types.items()):
                print(f"  - {chunk_type}: {count} chunks")
        else:
            split_java_docs = []
            print("No Java documents to chunk")

        # Combine semantic Java chunks with non-Java documents
        result = split_java_docs + non_java_docs

        print(f"\n{'#' * 80}")
        print(f"ENHANCED PROJECT PROCESSING COMPLETE: {directory_path}")
        print(f"Total documents after processing: {len(result)}")
        print(f"  - Semantic Java chunks: {len(split_java_docs)}")
        print(f"  - Non-Java documents: {len(non_java_docs)}")
        print(f"{'#' * 80}\n")

        return result


# Example usage
if __name__ == "__main__":
    # Create the enhanced parser with configurable chunk size and overlap
    project_parser = EnhancedJavaProjectParser(
        chunk_size=1000,  # Maximum size for method chunks
        chunk_overlap=200  # Overlap between chunks for large methods
    )

    # Parse an entire project directory
    project_dir = "/Users/rishabhsharma/PycharmProjects/ecommerce-site/backend/app/chatbot/test"
    all_docs = project_parser.process_project(project_dir, recursive=True)

    print(f"Total documents processed: {len(all_docs)}")

    # Count document types with enhanced metadata
    java_chunks = [doc for doc in all_docs if doc.metadata.get("type") in
                   ["class", "method", "method_part", "field", "package", "imports"]]

    other_files = [doc for doc in all_docs if doc.metadata.get("type") not in
                   ["class", "method", "method_part", "field", "package", "imports"]]

    print(f"Java semantic chunks: {len(java_chunks)}")
    print(f"Other file documents: {len(other_files)}")
    
    # Sample chunk metadata for demonstration
    if java_chunks:
        print("\nSample enhanced metadata for a Java chunk:")
        sample_chunk = java_chunks[0]
        print(f"Type: {sample_chunk.metadata.get('type')}")
        print(f"Name: {sample_chunk.metadata.get('name')}")
        
        if 'full_qualified_name' in sample_chunk.metadata:
            print(f"Fully qualified name: {sample_chunk.metadata.get('full_qualified_name')}")
        
        if 'context_path' in sample_chunk.metadata:
            print(f"Context path: {sample_chunk.metadata.get('context_path')}")
        
        if 'signature' in sample_chunk.metadata:
            print(f"Signature: {sample_chunk.metadata.get('signature')}")
        
        if 'references' in sample_chunk.metadata and sample_chunk.metadata['references']:
            print(f"References: {', '.join(sample_chunk.metadata['references'])}")
            
        if 'javadoc_summary' in sample_chunk.metadata:
            print(f"Javadoc summary: {sample_chunk.metadata.get('javadoc_summary')}")
