def test_deployment_shopper(terraform_output):
    assert "market-data-" in terraform_output["s3_bucket_name"]["value"]
