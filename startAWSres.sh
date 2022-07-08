#!/bin/bash

aws iam create-role --role-name lambdarole --assume-role-policy-document file://settings/role_policy.json --query 'Role.Arn' --endpoint-url=http://localhost:4566
aws iam put-role-policy --role-name lambdarole --policy-name lambdapolicy --policy-document file://settings/policy.json --endpoint-url=http://localhost:4566

zip activeMonitoring.zip settings/lambda-func/activeMonitoring.py

aws lambda create-function \
--function-name activeMonitoring \
--zip-file fileb://activeMonitoring.zip \
--handler settings/lambda-func/activeMonitoring.lambda_handler \
--runtime python3.6 \
--role arn:aws:iam::000000000000:role/lambdarole \
--endpoint-url=http://localhost:4566

zip passDataInDynamo.zip settings/lambda-func/passDataInDynamo.py

aws lambda create-function \
--function-name passDataInDynamo \
--zip-file fileb://passDataInDynamo.zip \
--handler settings/lambda-func/passDataInDynamo.lambda_handler \
--runtime python3.6 \
--role arn:aws:iam::000000000000:role/lambdarole \
--endpoint-url=http://localhost:4566

zip activeOutputSensor.zip settings/lambda-func/activeOutputSensor.py

aws lambda create-function \
--function-name activeOutputSensor \
--zip-file fileb://activeOutputSensor.zip \
--handler settings/lambda-func/activeOutputSensor.lambda_handler \
--runtime python3.6 \
--role arn:aws:iam::000000000000:role/lambdarole \
--endpoint-url=http://localhost:4566

zip switchOffActuator.zip settings/lambda-func/switchOffActuator.py

aws lambda create-function \
--function-name switchOffActuator \
--zip-file fileb://switchOffActuator.zip \
--handler settings/lambda-func/switchOffActuator.lambda_handler \
--runtime python3.6 \
--role arn:aws:iam::000000000000:role/lambdarole \
--endpoint-url=http://localhost:4566

#########################################################################
#########################################################################
#activeMonitoring
aws events put-rule \
--name simulateIOTsensors \
--schedule-expression 'rate(3 minutes)' \
--endpoint-url=http://localhost:4566

aws lambda add-permission \
--function-name activeMonitoring \
--statement-id simulateIOTsensors \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn arn:aws:events:eu-west-1:000000000000:rule/simulateIOTsensors \
--endpoint-url=http://localhost:4566

aws events put-targets \
--rule simulateIOTsensors \
--targets file://settings/targets/targets_activeMonitoring.json \
--endpoint-url=http://localhost:4566

#passDataInDynamo
aws events put-rule \
--name passData \
--schedule-expression 'rate(4 minutes)' \
--endpoint-url=http://localhost:4566

aws lambda add-permission \
--function-name passDataInDynamo \
--statement-id passData \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn arn:aws:events:eu-west-1:000000000000:rule/passData \
--endpoint-url=http://localhost:4566

aws events put-targets \
--rule passData \
--targets file://settings/targets/targets_passDatainDynamo.json \
--endpoint-url=http://localhost:4566

#activeOutputSensor actuators
aws events put-rule \
--name activeActuators \
--schedule-expression 'rate(5 minutes)' \
--endpoint-url=http://localhost:4566

aws lambda add-permission \
--function-name activeOutputSensor \
--statement-id activeActuators \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn arn:aws:events:eu-west-1:000000000000:rule/activeActuators \
--endpoint-url=http://localhost:4566

aws events put-targets \
--rule activeActuators \
--targets file://settings/targets/targets_activeActuators.json \
--endpoint-url=http://localhost:4566

#switchOffActuator
aws events put-rule \
--name OFFactuators \
--schedule-expression 'rate(1 minutes)' \
--endpoint-url=http://localhost:4566

aws lambda add-permission \
--function-name switchOffActuator \
--statement-id OFFactuators \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn arn:aws:events:eu-west-1:000000000000:rule/OFFactuators \
--endpoint-url=http://localhost:4566

aws events put-targets \
--rule OFFactuators \
--targets file://settings/targets/targets_switchOffactuator.json \
--endpoint-url=http://localhost:4566

#for show tables of dynamodb in browser
####https://github.com/aaronshaf/dynamodb-admin
####DYNAMO_ENDPOINT=http://0.0.0.0:4566 dynamodb-admin
