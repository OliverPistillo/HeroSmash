class_name CombatJson
extends RefCounted

static func normalize(value: Variant) -> Variant:
	if value is float and is_finite(value) and value == floor(value): return int(value)
	if value is Array:
		var result: Array = []
		for item: Variant in value: result.append(normalize(item))
		return result
	if value is Dictionary:
		var result: Dictionary = {}
		for key: String in value: result[key] = normalize(value[key])
		return result
	return value

static func encode(value: Variant) -> String:
	return JSON.stringify(normalize(value), "", true, true)

static func digest(value: Variant) -> String:
	return encode(value).sha256_text()

static func integer(value: Variant, minimum: int = 0, maximum: int = 1000000000) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and float(value) == floor(float(value)) and value >= minimum and value <= maximum

static func ceil_div(value: int, divisor: int) -> int:
	if value <= 0: return 0
	@warning_ignore("integer_division")
	return (value + divisor - 1) / divisor

static func read_file(path: String) -> Variant:
	var file: FileAccess = FileAccess.open(path, FileAccess.READ)
	if file == null or file.get_length() > 100000000: return null
	var parser: JSON = JSON.new()
	if parser.parse(file.get_as_text()) != OK: return null
	return normalize(parser.data)
