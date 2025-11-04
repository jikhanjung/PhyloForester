# Docstring Style Guide

PhyloForester uses **Google-style docstrings** as defined in the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

## Why Google Style?

- Clean, readable format
- Well-supported by Sphinx via Napoleon extension
- Clear separation of sections
- Good balance between verbosity and brevity

## General Rules

1. All public modules, classes, functions, and methods must have docstrings
2. Use triple double-quotes `""" """` for all docstrings
3. First line should be a one-sentence summary (imperative mood)
4. Leave a blank line after the summary if there's more content
5. Use proper grammar, punctuation, and complete sentences

## Module Docstrings

Place at the top of each module file:

```python
"""Brief one-line summary of the module.

More detailed explanation of what the module does. Can span
multiple lines and paragraphs if needed.

Typical usage example:

    from module import function
    result = function(arg1, arg2)
"""
```

## Function and Method Docstrings

### Basic Structure

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """Brief one-line summary of what the function does.

    More detailed explanation if needed. Explain the purpose,
    behavior, and any important details about the function.

    Args:
        param1: Description of param1. Should explain what it is,
            valid values, and any constraints.
        param2: Description of param2. Default values are shown
            in the function signature. Defaults to 0.

    Returns:
        Description of the return value. What does it mean?

    Raises:
        ValueError: Description of when this error is raised.
        TypeError: Description of when this error is raised.

    Example:
        Basic usage example showing how to call the function::

            result = function_name("test", 42)
            if result:
                print("Success!")

    Note:
        Any additional notes, caveats, or important information
        that doesn't fit in other sections.
    """
    pass
```

### Simple Function (No Arguments or Return Value)

```python
def simple_function() -> None:
    """Brief description of what this function does."""
    pass
```

### Function with Only Args

```python
def process_data(data: list[str], validate: bool = True) -> list[str]:
    """Process input data and return cleaned results.

    Args:
        data: List of strings to process. Each string should be
            a valid identifier.
        validate: Whether to validate input before processing.
            Defaults to True.

    Returns:
        List of processed strings with whitespace removed and
        converted to lowercase.
    """
    pass
```

### Function with Only Returns

```python
def get_default_path() -> Path:
    """Get the default application data directory path.

    Returns:
        Path to the default data directory. Creates the directory
        if it doesn't exist.
    """
    pass
```

## Class Docstrings

### Class with __init__

```python
class MyClass:
    """Brief one-line summary of the class.

    More detailed explanation of what the class does, its purpose,
    and how it fits into the larger system.

    Attributes:
        attribute1: Description of public attribute1.
        attribute2: Description of public attribute2.

    Example:
        Basic usage example::

            obj = MyClass("value", 42)
            result = obj.do_something()
    """

    def __init__(self, param1: str, param2: int) -> None:
        """Initialize MyClass instance.

        Args:
            param1: Description of initialization parameter.
            param2: Description of initialization parameter.

        Raises:
            ValueError: If param2 is negative.
        """
        self.attribute1 = param1
        self.attribute2 = param2
```

### Class Methods

```python
    def public_method(self, arg: str) -> int:
        """Brief description of what this method does.

        Args:
            arg: Description of the argument.

        Returns:
            Description of return value.

        Raises:
            RuntimeError: If the operation fails.
        """
        pass

    def _private_method(self) -> None:
        """Private methods should also have docstrings.

        Even though private methods are not included in public
        documentation, they should still be documented for
        internal developers.
        """
        pass
```

## Property Docstrings

```python
@property
def my_property(self) -> str:
    """Brief description of what this property represents.

    Returns:
        Description of the property value.
    """
    return self._my_property

@my_property.setter
def my_property(self, value: str) -> None:
    """Set the property value.

    Args:
        value: New value for the property.

    Raises:
        ValueError: If value is invalid.
    """
    self._my_property = value
```

## Common Sections

### Args Section

- List each parameter on its own line
- Use consistent indentation (4 spaces)
- Don't repeat type information (already in type hints)
- Explain what the parameter is, valid values, constraints

```python
Args:
    file_path: Path to the input file. Must be a readable file.
    encoding: Character encoding for file reading. Common values
        are 'utf-8', 'latin-1'. Defaults to 'utf-8'.
    strict: If True, raise exception on parse errors. If False,
        log warnings and continue. Defaults to False.
```

### Returns Section

- Describe what the return value represents
- Explain the structure for complex return types
- Don't repeat the type (already in type hints)

```python
Returns:
    Dictionary mapping taxon names to character states. Each key
    is a string taxon name, and each value is a list of character
    state integers. Empty dict if no taxa found.
```

### Raises Section

- List specific exceptions that may be raised
- Explain under what conditions they're raised
- Don't document exceptions from called functions unless relevant

```python
Raises:
    FileNotFoundError: If the specified file doesn't exist.
    ValueError: If the file format is invalid or cannot be parsed.
    PermissionError: If the file cannot be read due to permissions.
```

### Example Section

- Show realistic usage examples
- Use `::` for code blocks (reStructuredText syntax)
- Keep examples concise but complete

```python
Example:
    Basic usage with default options::

        parser = NexusParser("data.nex")
        matrix = parser.parse()

    Advanced usage with options::

        parser = NexusParser("data.nex", strict=True)
        matrix = parser.parse()
        print(f"Loaded {len(matrix.taxa)} taxa")
```

### Note Section

- Use for caveats, warnings, or important information
- Alternative section names: `Note:`, `Warning:`, `See Also:`

```python
Note:
    This function modifies the input list in-place. If you need
    to preserve the original, pass a copy.

Warning:
    This operation can be slow for large datasets (>10,000 taxa).
    Consider using the batch processing function instead.

See Also:
    batch_process: Batch processing version of this function.
    validate_input: Function to validate input before processing.
```

## PyQt5-Specific Guidelines

### Slot Methods

```python
@pyqtSlot()
def on_button_clicked(self) -> None:
    """Handle button click event.

    This slot is connected to the clicked signal of the submit button.
    Validates input and initiates processing.
    """
    pass
```

### Signal Documentation

```python
class MyWidget(QWidget):
    """Custom widget with signals.

    Signals:
        dataChanged: Emitted when data is modified. Passes the new data
            as a dict argument.
        processingFinished: Emitted when background processing completes.
            Passes success status as a bool.
    """

    dataChanged = pyqtSignal(dict)
    processingFinished = pyqtSignal(bool)
```

## Type Hints and Docstrings

Since we use type hints, **do not repeat type information in docstrings**:

### ❌ Bad (Redundant Type Information)

```python
def process(data: list[str], count: int) -> dict[str, int]:
    """Process data.

    Args:
        data (list[str]): List of strings to process.
        count (int): Number of items to process.

    Returns:
        dict[str, int]: Dictionary of results.
    """
    pass
```

### ✅ Good (Type Hints Only, Docstring Describes Purpose)

```python
def process(data: list[str], count: int) -> dict[str, int]:
    """Process input data and count occurrences.

    Args:
        data: List of strings to analyze. Each string should be
            a valid identifier without whitespace.
        count: Maximum number of items to process. Remaining items
            are ignored.

    Returns:
        Mapping of unique strings to their occurrence counts.
        Only includes strings that appear more than once.
    """
    pass
```

## Peewee Model Documentation

For database models using Peewee:

```python
class PfProject(Model):
    """Project model representing a phylogenetic analysis project.

    Stores metadata about a project including name, description,
    creation date, and associated datamatrices. Projects are the
    top-level container in the application hierarchy.

    Attributes:
        project_name: Unique name of the project.
        project_description: Optional detailed description.
        date_created: Timestamp when project was created.
        date_modified: Timestamp of last modification.

    Relations:
        datamatrices: One-to-many relationship to PfDatamatrix.
            Cascade deletes when project is deleted.

    Example:
        Creating a new project::

            project = PfProject.create(
                project_name="My Analysis",
                project_description="Cambrian fauna study"
            )
            print(f"Created project {project.project_name}")
    """

    project_name = CharField(unique=True, max_length=255)
    project_description = TextField(null=True)
    date_created = DateTimeField(default=datetime.datetime.now)
    date_modified = DateTimeField(default=datetime.datetime.now)

    def get_datamatrix_count(self) -> int:
        """Get number of datamatrices in this project.

        Returns:
            Count of associated datamatrices.
        """
        return self.datamatrices.count()
```

## Tools and Validation

### Sphinx Build

Validate docstrings by building documentation:

```bash
cd docs
make html
```

Check for warnings about malformed docstrings.

### Ruff

Ruff checks for missing docstrings (rule D):

```bash
ruff check --select D .
```

### mypy

Type hints are validated by mypy:

```bash
mypy PfLogger.py version.py --strict
```

## Migration Strategy

For existing code without docstrings:

1. **Priority 1**: Public API (modules, classes, public methods)
2. **Priority 2**: Complex or non-obvious functions
3. **Priority 3**: Private methods and simple utility functions

When adding docstrings to existing code:
- Start with module-level docstrings
- Add class docstrings and `__init__` docstrings
- Add method docstrings for public methods
- Add function docstrings

## References

- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Sphinx Napoleon Extension](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)

## Summary Checklist

When writing docstrings, ask yourself:

- [ ] Does the summary line clearly state what this does?
- [ ] Are all parameters explained (purpose, not type)?
- [ ] Is the return value explained (meaning, not type)?
- [ ] Are exceptions documented with conditions?
- [ ] Is there an example for complex functions?
- [ ] Are there notes about side effects or caveats?
- [ ] Is the language clear and concise?
- [ ] Does it help someone understand how to use this code?
