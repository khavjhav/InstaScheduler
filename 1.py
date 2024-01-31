from bson import ObjectId
user = ObjectId("652d696246e5418fac34e99d")
id_string = str(user)
print(id_string)

desired_part = id_string[10:len(id_string)-2]
print(desired_part)