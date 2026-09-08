class_name EffectCapabilities
extends RefCounted

const TRIGGERS: Array[String] = ["combat_start", "basic_attack", "basic_hit", "skill_cast", "skill_hit", "damage_taken", "status_applied", "dodge", "heal", "interval", "combat_end"]
const ACTIONS: Array[String] = ["deal_damage", "modify_stat", "apply_status", "heal", "add_shield", "gain_energy", "special_handler"]
const BRANCHES: Array[String] = ["assault", "guardian", "essence", "rage", "ice", "toxin", "shield", "healing", "power", "precision", "wound", "dodge"]

static func validate_rules(rules: Array) -> Array[String]:
	var errors: Array[String] = []
	for rule: Dictionary in rules:
		var trigger: String = rule["trigger"]
		if not TRIGGERS.has(trigger):
			errors.append("unsupported_trigger: " + trigger)
		if (trigger == "interval") != (int(rule["interval_ms"]) > 0):
			errors.append("interval requires positive interval_ms only")
		if int(rule["loss_threshold_milli"]) != 0 and trigger != "damage_taken":
			errors.append("loss threshold requires damage_taken")
		var condition: Dictionary = rule["condition"]
		var allowed: Dictionary = {"always":TRIGGERS, "critical":["basic_hit", "skill_hit"], "regen":["heal"], "status":["status_applied"], "reflectable":["dodge"]}
		if not allowed[condition["kind"]].has(trigger):
			errors.append("condition incompatible with trigger")
		if (condition["kind"] == "status" and not BRANCHES.has(condition["value"])) or (condition["kind"] != "status" and condition["value"] != ""):
			errors.append("invalid condition value")
		for action: Dictionary in rule["actions"]:
			var kind: String = action["type"]
			if not ACTIONS.has(kind):
				errors.append("unsupported_action: " + kind)
			if action["formula"] != "flat" and kind != "heal":
				errors.append("formula only supported for heal")
			if action["formula"] == "flat" and (action["factor_bp"] != 0 or action["minimum"] != 0):
				errors.append("unused formula fields")
			if action["cap"] != 0 and kind != "modify_stat":
				errors.append("cap only supported for modify_stat")
			if action["handler"] != ("reflect_incoming_once" if kind == "special_handler" else ""):
				errors.append("unsupported_handler")
			var damage_kinds: Array = ["magic", "phys", "health_loss"] if kind == "deal_damage" else (["magic"] if kind == "special_handler" else ["none"])
			if not damage_kinds.has(action["damage_kind"]):
				errors.append("invalid damage kind")
			if kind == "modify_stat":
				if not [["base_damage_milli", "milli"], ["basic_damage_bonus_bp", "basis_points"]].has([action["field"], action["unit"]]):
					errors.append("unsupported stat/unit")
			elif kind in ["apply_status", "add_shield"]:
				if action["unit"] != "stacks" or not BRANCHES.has(action["field"]) or (kind == "add_shield" and action["field"] != "shield"):
					errors.append("invalid status stacks")
			elif action["unit"] != "milli" or action["field"] != "":
				errors.append("unexpected unit/field")
			if kind == "special_handler" and (trigger != "dodge" or condition["kind"] != "reflectable" or action["target"] != "opponent" or action["amount"] != 0):
				errors.append("reflect handler requires eligible dodge/opponent and event amount")
	return errors
