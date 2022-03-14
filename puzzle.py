import re


class Puzzle:
    """
    A word search puzzle is a square grid of letters and a list of words found somewhere in the grid.
    This solver was made as a complement to https://github.com/joshbduncan/word-search-generator
    """

    DIRECTIONS = {
        "N": {"x": 0, "y": -1},
        "NE": {"x": 1, "y": -1},
        "E": {"x": 1, "y": 0},
        "SE": {"x": 1, "y": 1},
        "S": {"x": 0, "y": 1},
        "SW": {"x": -1, "y": 1},
        "W": {"x": -1, "y": 0},
        "NW": {"x": -1, "y": -1},
    }

    def __init__(self, path):
        """
        Load a puzzle from a text file in the format produced by https://github.com/joshbduncan/word-search-generator
        """
        self.rows = []
        with open(path, "r") as f:
            lines = f.readlines()

            # find grid
            for i, line in enumerate(lines[2:], 2):
                row = line.strip("\n").split(",")
                if len(row) <= 1:
                    break
                self.rows.append(row)

            # find words
            for j, line in enumerate(lines[i:], 2):
                if "Find these words:" in line:
                    part = line.split(":", 1)[1].strip(' "\n')
                    self.words = part.split(", ")
                    break

            # find answers (used to validate the solution)
            for line in lines[i + j :]:
                if "Answer Key:" in line:
                    self.answers = dict(re.findall(r"([A-Z]+) ([NSEW]{1,2} @ \([0-9]+, [0-9]+\))", line))
                    break

        # validate
        if not self.rows:
            raise Exception("did not find rows")
        if not self.words:
            raise Exception("did not find words")

    def __str__(self):
        return f"Puzzle: {self.size} size, {len(self.words)} words"

    @property
    def size(self):
        return len(self.rows)

    def display(self, answers=None):
        """
        Answers must be dicts with the word as the key and the answer as the value.
        Answer syntax is as found in https://github.com/joshbduncan/word-search-generator
        Example: "E @ (12, 6)" means start at y=12, x=6 (1-indexed) and read Eastward
        """
        if answers:
            header = "** WORD SEARCH PUZZLE: ANSWERS **"

            # create answer grid
            rows = [["." for _ in range(self.size)] for _ in range(self.size)]  # blank grid
            answer_re = re.compile(r"([NSEW]{1,2}) @ \(([0-9]+), ([0-9]+)\)")
            for word, answer in answers.items():
                for direction, y, x in answer_re.findall(answer):
                    x, y = int(x) - 1, int(y) - 1
                    for letter in word:
                        rows[y][x] = letter
                        x += self.DIRECTIONS[direction]["x"]
                        y += self.DIRECTIONS[direction]["y"]
            words = ", ".join(f"{word} {location}" for word, location in answers.items())
        else:
            header = "** WORD SEARCH PUZZLE **"
            rows = self.rows
            words = ", ".join(self.words)
        grid = "\n".join(" ".join(cell for cell in row) for row in rows)
        print(f"{header}\n\n{grid}\n\nWords: {words}\n")

    def get_cell(self, x, y):
        if x < 0 or y < 0 or x >= self.size or y >= self.size:
            return None
        return self.rows[y][x]

    def solve(self):
        answers = {word: self.find_word(word) for word in self.words}
        assert answers == self.answers  # validate
        return answers

    def find_word(self, word):
        """Return the x, y coordinates and direction of the word's location in the puzzle grid."""
        for y in range(self.size):
            for x in range(self.size):
                cell = self.get_cell(x, y)
                if cell == word[0]:
                    for direction in self.DIRECTIONS:
                        if self.find_rest(direction, x, y, word[1:]):
                            return f"{direction} @ ({y + 1}, {x + 1})"  # translate to 1-indexed
        raise Exception(f"word '{word}' not found")

    def find_rest(self, direction, x, y, rest):
        """Move in direction checking each letter in the puzzle grid for a match against the rest of the word."""
        if not rest:
            return True
        x += self.DIRECTIONS[direction]["x"]
        y += self.DIRECTIONS[direction]["y"]
        cell = self.get_cell(x, y)
        if not cell or cell != rest[0]:
            return None
        return self.find_rest(direction, x, y, rest[1:])


if __name__ == "__main__":
    import os

    directory = os.path.join(os.path.dirname(__file__), "samples")
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        puzzle = Puzzle(path)
        puzzle.display()
        answers = puzzle.solve()
        puzzle.display(answers)
