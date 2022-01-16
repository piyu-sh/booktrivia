
# first create table in local dynamodb to test, command below
# aws dynamodb create-table --cli-input-json file://booksNFactsTableConfig.json --endpoint-url http://localhost:8000 --region=ap-south-1


# read book facts grouped file 
# skip already written facts, maintain in other file, i think ID should be sufficient to save but lets think about it more
# write new facts to dynamodb in batches
