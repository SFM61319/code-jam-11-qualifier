from enum import auto, StrEnum
import warnings


MAX_QUOTE_LENGTH = 50


class VariantMode(StrEnum):
    """
    Enum representing the different modes that a quote can be transformed into.

    - `NORMAL`: The quote is returned as-is, without any transformation.
    - `UWU`: The quote is transformed into the "UwU" style.
    - `PIGLATIN`: The quote is transformed into Pig Latin.
    """

    NORMAL = auto()
    UWU = auto()
    PIGLATIN = auto()


class DuplicateError(Exception):
    """
    Error raised when there is an attempt to add a duplicate entry to a database
    """


class Quote:
    """
    Represents a quote with a specified transformation mode.

    The `Quote` class encapsulates a quote string and a `VariantMode`
    that determines how the quote should be transformed. The
    `_create_variant()` method is responsible for applying the
    appropriate transformation to the quote based on the specified mode.
    """

    quote: str
    mode: VariantMode

    def __init__(self, quote: str, mode: VariantMode) -> None:
        self.quote = quote
        self.mode = mode

    def __str__(self) -> str:
        return self.quote

    def _create_variant(self) -> str:
        """
        Transforms `self.quote` to the appropriate variant indicated by
        `self.mode` and returns the result.
        """

        match self.mode:
            case VariantMode.NORMAL:
                return self.quote

            case VariantMode.UWU:
                return uwuify(self.quote)

            case VariantMode.PIGLATIN:
                raise NotImplementedError("Pig Latin variant not implemented")


def run_command(command: str) -> None:
    """
    Will be given a command from a user. The command will be parsed and
    executed appropriately.

    Current supported commands:
        - `quote`: creates and adds a new quote
        - `quote uwu`: uwu-ifys the new quote and then adds it
        - `quote piglatin`: piglatin-ifys the new quote and then adds it
        - `quote list`: print a formatted string that lists the current
           quotes to be displayed in discord flavored markdown
    """

    match command:
        case command if command.startswith("quote uwu"):
            raw_quote = command[11:-1]
            uwuified_quote = uwuify(raw_quote)

            add_quote(uwuified_quote, VariantMode.UWU)

        case command if command.startswith("quote piglatin"):
            raw_quote = command[16:-1]
            raise NotImplementedError("Command not implemented")

        case command if command.startswith("quote list"):
            formatted_quotes = list_formatted_quotes()
            print(formatted_quotes)

        case command if (
            (command.startswith('quote "') and command.endswith('"'))
            or (command.startswith("quote “") and command.endswith("”"))
        ):
            raw_quote = command[7:-1]
            add_quote(raw_quote, VariantMode.NORMAL)

        case _:
            raise ValueError("Invalid command")


def list_formatted_quotes() -> str:
    """
    Returns a formatted string that lists all the current quotes in the database.

    The quotes are formatted with a bullet point (`-`) prefix, one quote per line.

    Returns:
        str: The formatted string.
    """

    return "\n".join(f"- {quote}" for quote in Database.get_quotes())


def add_quote(quote: str, mode: VariantMode) -> None:
    """
    Adds a new quote to the database.

    Args:
        quote (str): The new quote to add.
        mode (VariantMode): The `VariantMode` to apply to the new quote.

    Raises:
        - `ValueError` if the quote is longer than 50 characters.
    """

    if len(quote) > MAX_QUOTE_LENGTH:
        raise ValueError("Quote is too long")

    try:
        Database.add_quote(Quote(quote, mode))
    except DuplicateError:
        print("Quote has already been added previously")


def uwuify(quote: str) -> str:
    """
    UwUifies the given quote.

    Args:
        quote (str): The quote to uwuify.

    Returns:
        str: The uwuified quote.
    """

    partially_transformed_quote = (
        quote.replace("L", "W").replace("l", "w").replace("R", "W").replace("r", "w")
    )
    fully_transformed_quote = " ".join(
        (
            f"U-{word}"
            if word.startswith("U")
            else f"u-{word}" if word.startswith("u") else word
        )
        for word in partially_transformed_quote.split(" ")
    )

    transformed_quote = fully_transformed_quote
    if len(fully_transformed_quote) > MAX_QUOTE_LENGTH:
        transformed_quote = partially_transformed_quote
        warnings.warn("Quote too long, only partially transformed")

    if transformed_quote == quote:
        raise ValueError("Quote was not modified")

    return transformed_quote


class Database:
    """
    Provides a simple in-memory database for storing and retrieving
    `Quote` objects.

    The `Database` class manages a list of `Quote` objects, providing methods
    to add new quotes and retrieve the current list of quotes.

    If an attempt is made to add a duplicate quote
    (based on the string representation of the `Quote`
    object), a `DuplicateError` exception will be raised.
    """

    quotes: list[Quote] = []

    @classmethod
    def get_quotes(cls) -> list[str]:
        """
        Returns current quotes in a list.
        """

        return [str(quote) for quote in cls.quotes]

    @classmethod
    def add_quote(cls, quote: Quote) -> None:
        """
        Adds a quote. Will raise a `DuplicateError` if an error occurs.
        """

        if str(quote) in cls.get_quotes():
            raise DuplicateError

        cls.quotes.append(quote)
