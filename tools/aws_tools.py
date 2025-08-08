from typing import List, Union, Dict
from datetime import date
from mcp.server.fastmcp import FastMCP

import boto3

mcp = FastMCP(name="aws_tools", stateless_http=True)


@mcp.tool(description="Retrieve contents of a file in an S3 bucket")
def get_s3_object_data(bucket_name: str, object_key: str) -> str:
    s3 = boto3.client("s3")
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        content = response["Body"].read().decode("utf-8")
        return content
    except Exception as e:
        return f"Error reading {object_key} from {bucket_name}: {str(e)}"


@mcp.tool(description="List all S3 buckets in AWS account")
def list_s3_buckets() -> List[str]:
    s3 = boto3.client("s3")
    response = s3.list_buckets()
    buckets = [bucket["Name"] for bucket in response.get("Buckets", [])]
    return buckets or ["No S3 buckets found."]


@mcp.tool(description="Get the AWS region of a specific S3 bucket")
def get_s3_bucket_region(bucket_name: str) -> str:
    s3 = boto3.client("s3")
    response = s3.get_bucket_location(Bucket=bucket_name)
    return response.get("LocationConstraint") or "us-east-1"


@mcp.tool(description="List objects in a given S3 bucket, max up to max_keys")
def list_objects_in_bucket(bucket_name: str, max_keys: int = 10) -> List[str]:
    s3 = boto3.client("s3")
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=max_keys)
        contents = response.get("Contents", [])
        return [obj["Key"] for obj in contents] or ["No objects found."]
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool(description="Estimate total size and object count of an S3 bucket")
def get_s3_bucket_size_summary(bucket_name: str) -> Union[str, Dict[str, Union[int, str]]]:
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    total_size = 0
    object_count = 0
    try:
        for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get("Contents", []):
                object_count += 1
                total_size += obj["Size"]
        return {
            "bucket": bucket_name,
            "total_objects": object_count,
            "total_size_mb": f"{total_size / (1024 ** 2):.2f} MB"
        }
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(description="Get current month's AWS cost breakdown by service")
def get_monthly_cost_breakdown() -> dict:
    ce = boto3.client("ce")
    today = date.today()
    start = today.replace(day=1).isoformat()
    end = today.isoformat()

    try:
        response = ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
        )
        results = response["ResultsByTime"][0]
        total = 0.0
        breakdown = {}
        for group in results["Groups"]:
            service = group["Keys"][0]
            amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
            breakdown[service] = round(amount, 2)
            total += amount
        return {
            "time_period": f"{start} to {end}",
            "total_cost_usd": round(total, 2),
            "by_service": breakdown
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(description="Forecast total AWS spending for current month based on usage to date")
def get_total_monthly_cost_forecast() -> dict:
    ce = boto3.client("ce")
    today = date.today()
    start_of_month = today.replace(day=1)

    try:
        actual_response = ce.get_cost_and_usage(
            TimePeriod={"Start": start_of_month.isoformat(), "End": today.isoformat()},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"]
        )
        actual = float(actual_response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"])
    except Exception as e:
        return {"error": f"Error getting actual cost: {str(e)}"}

    if today.month == 12:
        end_of_month = date(today.year + 1, 1, 1)
    else:
        end_of_month = date(today.year, today.month + 1, 1)

    try:
        forecast_response = ce.get_cost_forecast(
            TimePeriod={"Start": today.isoformat(), "End": end_of_month.isoformat()},
            Granularity="MONTHLY",
            Metric="UNBLENDED_COST"
        )
        forecast = float(forecast_response["ForecastResultsByTime"][0]["MeanValue"])
    except Exception as e:
        return {"error": f"Error getting forecasted cost: {str(e)}"}

    total = actual + forecast

    return {
        "actual_to_date_usd": round(actual, 2),
        "forecast_remaining_usd": round(forecast, 2),
        "forecast_total_month_usd": round(total, 2),
        "time_period": f"{start_of_month} to {end_of_month}"
    }

aws_tools = list(mcp._tool_manager._tools.values())
