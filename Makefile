.PHONY: deploy-test-resources

deploy-test-resources:
	sam deploy \
		--template-file ./deployments/test-resources.yaml \
		--stack-name cfn-docgen-test-resources