import csv
from typing import *
from dataclasses import dataclass
import unittest
import math
import sys


@dataclass(frozen=True)
class Row:
    name: str
    year: int
    electricity_and_heat_co2_emissions: Optional[float]
    electricity_and_heat_co2_emissions_per_capita: Optional[float]
    energy_co2_emissions: Optional[float]
    energy_co2_emissions_per_capita: Optional[float]
    total_co2_emissions_excluding_lucf: Optional[float]
    total_co2_emissions_excluding_lucf_per_capita: Optional[float]


@dataclass(frozen=True)
class RLNode:
    first: Row
    rest: Optional["RLNode"] = None


LinkedList: TypeAlias = Union[RLNode, None]
ll_file_rows: LinkedList


# converts the csv file line from an array to a row
def array_to_row(arr: List[str]) -> Row:
    try:
        row = Row(
            arr[0],
            int(arr[1]),
            float(arr[2]),
            float(arr[3]),
            float(arr[4]),
            float(arr[5]),
            float(arr[6]),
            float(arr[7]),
        )
    except TypeError:
        row = Row(
            arr[0],
            int(arr[1]),
            str(arr[2]),
            float(arr[3]),
            float(arr[4]),
            float(arr[5]),
            float(arr[6]),
            float(arr[7]),
        )

    if arr[0] == "country":
        return "header"
    else:
        return row


# read in all the lines from a given csv file and gives a linked list of each row
def read_csv_lines(filename: str) -> Optional[RLNode]:
    head: Optional[RLNode] = None

    with open(filename, newline="") as csvfile:  # binds the name csvfile to the file
        lines = csv.reader(csvfile)

        next(lines)  # skip header

        for line in lines:
            new_row: Row = array_to_row(line)
            head = RLNode(new_row, head)

    return head


# finds the length of a linked list of rows
def listlen(ll: LinkedList) -> int:
    match ll:
        case None:
            return 0
        case RLNode(_, r):
            return 1 + listlen(r)


FieldName = Literal[
    "country",
    "year",
    "electricity_and_heat_co2_emissions",
    "electricity_and_heat_co2_emissions_per_capita",
    "energy_co2_emissions",
    "energy_co2_emissions_per_capita",
    "total_co2_emissions_excluding_lucf",
    "total_co2_emissions_excluding_lucf_per_capita",
]

CompType = Literal["less_than", "equal", "greater_than"]

NUMERIC_FIELDS = {
    "year",
    "electricity_and_heat_co2_emissions",
    "electricity_and_heat_co2_emissions_per_capita",
    "energy_co2_emissions",
    "energy_co2_emissions_per_capita",
    "total_co2_emissions_excluding_lucf",
    "total_co2_emissions_excluding_lucf_per_capita",
}


def filter(
    rows: Optional[RLNode],
    field: FieldName,
    comp: CompType,
    value: object,
) -> Optional[RLNode]:
    """
    Purpose:
      Filter a linked list of Row objects by comparing a named field to a value.

    Params:
      rows: Optional[RLNode] -- head of the linked list
      field: FieldName -- one of the allowed column names
      comp: CompType -- "less_than" | "equal" | "greater_than"
      value: object -- comparison value (str for country, int/float for numeric fields)

    Returns:
      Optional[RLNode] -- head of new linked list (preserves original order).
    """
    # Validate combinations
    if field == "country":
        if comp != "equal":
            raise ValueError("country field only supports 'equal' comparison")
        if not isinstance(value, str):
            raise ValueError("country comparison value must be a string")
    else:
        # numeric fields: only less_than / greater_than are allowed for measurements.
        if comp == "equal":
            raise ValueError(f"field {field!r} does not support 'equal' comparison")


def answer_1(rows: Optional[RLNode]) -> int:
    """
    Purpose: Return the number of countries in the dataset.
    """
    # pick a year that definitely exists in sample-file.csv
    rows_2000 = filter(rows, "year", "equal", 2000)
    return listlen(rows_2000)


def answer_2(rows: Optional[RLNode]) -> Optional[RLNode]:
    """
    Purpose: Return all rows associated with Mexico.
    """
    return filter(rows, "country", "equal", "Mexico")


def answer_3(rows: Optional[RLNode]) -> Optional[RLNode]:
    """
    Purpose: Countries with higher per-capita total emissions than the US in 1990.
    """
    us_1990 = filter(rows, "country", "equal", "United States")
    us_1990 = filter(us_1990, "year", "equal", 1990)

    if us_1990 is None:
        return None

    us_value = us_1990.first.total_co2_emissions_excluding_lucf_per_capita

    all_1990 = filter(rows, "year", "equal", 1990)
    return filter(
        all_1990,
        "total_co2_emissions_excluding_lucf_per_capita",
        "greater_than",
        us_value,
    )


def answer_4(rows: Optional[RLNode]) -> Optional[RLNode]:
    """
    Purpose: Countries with higher per-capita total emissions than the US in 2020.
    """
    us_2020 = filter(rows, "country", "equal", "United States")
    us_2020 = filter(us_2020, "year", "equal", 2020)

    if us_2020 is None:
        return None

    us_value = us_2020.first.total_co2_emissions_excluding_lucf_per_capita

    all_2020 = filter(rows, "year", "equal", 2020)
    return filter(
        all_2020,
        "total_co2_emissions_excluding_lucf_per_capita",
        "greater_than",
        us_value,
    )


def answer_5(rows: Optional[RLNode]) -> Optional[float]:
    """
    Purpose: Return the approximate population of Luxembourg in 2014.
    """
    lux = filter(rows, "country", "equal", "Luxembourg")
    lux_2014 = filter(lux, "year", "equal", 2014)

    if lux_2014 is None:
        return None

    r = lux_2014.first
    return (
        r.total_co2_emissions_excluding_lucf
        / r.total_co2_emissions_excluding_lucf_per_capita
    )


def answer_6(rows: Optional[RLNode]) -> Optional[float]:
    """
    Purpose: Return the multiplier increase in China’s electricity-and-heat emissions
    from 1990 to 2020.
    """
    china = filter(rows, "country", "equal", "China")

    c1990 = filter(china, "year", "equal", 1990)
    c2020 = filter(china, "year", "equal", 2020)

    if c1990 is None or c2020 is None:
        return None

    e1990 = c1990.first.electricity_and_heat_co2_emissions
    e2020 = c2020.first.electricity_and_heat_co2_emissions

    return e2020 / e1990


def answer_7(rows: Optional[RLNode]) -> Optional[float]:
    """
    Purpose: Project China’s electricity-and-heat emissions in 2070.
    """
    china = filter(rows, "country", "equal", "China")

    c1990 = filter(china, "year", "equal", 1990)
    c2020 = filter(china, "year", "equal", 2020)

    if c1990 is None or c2020 is None:
        return None

    e1990 = c1990.first.electricity_and_heat_co2_emissions
    e2020 = c2020.first.electricity_and_heat_co2_emissions

    growth_rate = (e2020 / e1990) ** (1 / 30)
    return e2020 * (growth_rate**50)


class Tests(unittest.TestCase):
    def test_filter_country_equal(self):
        # All rows in sample-file.csv are Lithuania; filtering for Lithuania should return all rows.
        ll = read_csv_lines("sample_file.csv")
        res = filter(ll, "country", "equal", "Lithuania")
        # Expect same length as original

    def test_listlen_empty(self):
        # Empty linked list
        ll = None
        self.assertEqual(listlen(ll), 0)

    def test_listlen_sample_file(self):
        # Linked list created from sample-file.csv
        ll = read_csv_lines("sample_file.csv")

        # sample-file.csv contains 10 data rows (excluding header)
        self.assertEqual(listlen(ll), 10)

    def test_listlen_after_traversal(self):
        # Ensure listlen does not depend on traversal side effects
        ll = read_csv_lines("sample_file.csv")

        # Traverse part of the list
        cur = ll
        cur = cur.rest  # move to second node
        cur = cur.rest  # move to third node

        # Length of original list should still be unchanged
        self.assertEqual(listlen(ll), 10)

    def test_read_csv_fifth_node(self):
        ll = read_csv_lines("sample_file.csv")

        # Traverse to the 5th node (1-based)
        cur = ll
        for _ in range(4):
            self.assertIsNotNone(cur)
            cur = cur.rest

        # Now cur is the 5th node
        self.assertIsNotNone(cur)
        self.assertIsInstance(cur.first, Row)

        # Check expected values from the CSV
        self.assertEqual(cur.first.name, "Lithuania")
        self.assertEqual(cur.first.year, 1999)
        self.assertAlmostEqual(cur.first.electricity_and_heat_co2_emissions, 6.05)

    def test_read_csv_node_contains_row(self):
        ll = read_csv_lines("sample_file.csv")

        # Head exists and is an RLNode
        self.assertIsNotNone(ll)
        self.assertIsInstance(ll, RLNode)

        # The data stored in the node is a Row
        self.assertIsInstance(ll.first, Row)

        # Sanity-check some Row fields
        self.assertEqual(ll.first.name, "Lithuania")
        self.assertEqual(ll.first.year, 2003)

    def test_read_csv_second_node_contains_row(self):
        ll = read_csv_lines("sample_file.csv")

        # Second node exists
        self.assertIsNotNone(ll)
        self.assertIsNotNone(ll.rest)

        second_node = ll.rest

        # Second node is also an RLNode
        self.assertIsInstance(second_node, RLNode)

        # And it also stores a Row
        self.assertIsInstance(second_node.first, Row)

        # Check expected values from the CSV
        self.assertEqual(second_node.first.name, "Lithuania")
        self.assertEqual(second_node.first.year, 2002)


if __name__ == "__main__":
    unittest.main()
