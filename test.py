dic = " or ".join([f"contains(text(), '{course}')" for course in ["ECEN311", "ECEN305"]])

print(dic)