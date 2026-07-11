# Стандартизация марок и моделей автомобилей в БД
Скрипт для автоматической стандартизации данных. Читает JSON словарь и сопоставляет марки машин с базой данных для дальнейшей сегментации базы по маркам и моделям автомобилей

# Vehicle Data Enrichment

> Python tool for automatic vehicle brand and model recognition from unstructured text data.

## Description

This project processes raw customer vehicle data and automatically detects vehicle brands, models and manufacturer countries.

The script converts messy vehicle descriptions from Excel files into structured analytical data using dictionaries, regular expressions and external vehicle reference data.

Important:
The project requires a vehicle reference JSON file containing brands and models.
Without this dictionary only manual replacement rules will work.

## Business Goal

The main objective is to transform unstructured customer vehicle information into clean data suitable for analytics.

The analysis helps answer:

- Which vehicle brands customers use
- Which countries manufacturers belong to
- What vehicle models are most common
- How customer base is distributed by vehicles

## Features

- Excel file processing
- Vehicle reference JSON parsing
- Text cleaning and normalization
- Regular expression matching
- Custom replacement dictionary
- Vehicle brand recognition
- Vehicle model recognition
- Manufacturer country detection
- Customer aggregation
- Automatic Excel report generation
- Telegram execution notifications

## Tech Stack

- Python
- pandas
- NumPy
- regex
- requests
- openpyxl
- tqdm
- pyTelegramBotAPI
- python-dotenv

## How It Works

1. Loads customer Excel files
2. Loads vehicle dictionary from JSON
3. Cleans vehicle descriptions
4. Applies manual correction rules
5. Searches matching vehicle brands
6. Searches valid models for detected brands
7. Adds structured fields:
   - brand
   - model
   - country
8. Generates analytical Excel sheets

## Example / Demo

### Input

Excel file:

Customer | Vehicle

Example:

123456789 | BMW X5 3.0 Diesel

### Output

Structured data:

Brand: BMW

Model: X5

Country: Germany


Generated reports:

- Full recognition result
- Customers by country
- Customers by brand
- Unique customers by vehicle category

## Use Case

This project can be used for:

- data cleaning
- CRM enrichment
- customer analytics
- vehicle analytics
- automatic classification
