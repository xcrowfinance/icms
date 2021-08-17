import io
from dataclasses import dataclass, field
from typing import Optional, Union

import xlsxwriter


@dataclass
class XlsxHeaderData:
    data: list[str] = field(default_factory=list)
    styles: dict[str, Union[bool, str, int]] = field(default_factory=dict)


@dataclass
class XlsxConfig:
    header: XlsxHeaderData = field(repr=False, default=XlsxHeaderData())
    column_width: Optional[int] = field(repr=False, default=None)
    sheet_name: str = field(default_factory=str)


def generate_xlsx_file(config: XlsxConfig) -> bytes:
    output = io.BytesIO()
    with xlsxwriter.Workbook(output) as workbook:
        worksheet = workbook.add_worksheet(config.sheet_name)
        header_style = workbook.add_format(config.header.styles)
        for column, value in enumerate(config.header.data):
            worksheet.write(0, column, value, header_style)

        columns = len(config.header.data)
        if config.column_width and columns:
            worksheet.set_column(0, columns - 1, config.column_width)

    xlsx_data = output.getvalue()
    return xlsx_data