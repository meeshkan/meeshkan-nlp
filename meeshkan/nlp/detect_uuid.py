import uuid

good_list_uuid=[]
for i in range(5):
    good_list_uuid.append(str(uuid.uuid4()))
#print(good_list_uuid)

bad_list_uuid=['f030c4c11e-41c1-a7eb-3425c53f06d3', '181d4a62-df3e-4e9d-91d8-959b3cf3b', '134479a9-ba45-9d6bfb68051e', 'e2ce9aec-12f6-49f2-a655']


'''while True:
    val = input()
'''

def is_valid_uuid(id):
    try:
        uuid.UUID(str(id))
        return True
    except ValueError:
        return False

'''for good in good_list_uuid:
    print('uuid examples')
    print(good, is_valid_uuid(good))

for bad in bad_list_uuid:
    print('not UUID examples')
    print(bad, is_valid_uuid(bad))
'''
