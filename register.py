from python_freeipa import Client
client = Client('ipa.demo1.freeipa.org', version='2.215')
client.login('admin', 'Secret123')
user = client.user_add('test3', 'John', 'Doe', 'John Doe',mail="test@test", preferred_language='EN')
print(user)
