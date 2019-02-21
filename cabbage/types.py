import typing as t

JSON = t.Union[str, int, float, bool, None, t.Mapping[str, "JSON"], t.List["JSON"]]
