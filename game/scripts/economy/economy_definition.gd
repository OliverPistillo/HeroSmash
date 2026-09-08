class_name EconomyDefinition
extends CanonicalDefinition
## Constants only: this API does not decide interest/HP-loss/shop formulas.

func constants() -> Dictionary[String, int]:
	var result: Dictionary[String, int] = {}
	for key: String in _record["values"]:
		if key != "branch_thresholds":
			result[key] = int(_record["values"][key])
	return result

func branch_thresholds() -> Array[int]:
	var result: Array[int] = []
	for value: int in _record["values"]["branch_thresholds"]:
		result.append(value)
	return result
