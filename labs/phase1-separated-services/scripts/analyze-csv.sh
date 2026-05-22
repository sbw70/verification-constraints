#!/bin/bash

CSV="evidence/csv/500-comparison.csv"

echo
echo "========================================="
echo " CSV ANALYSIS"
echo "========================================="

echo
echo "Provider-First Gateway Average:"
awk -F, 'NR>1 {sum+=$2} END {print sum/(NR-1) " ms"}' "$CSV"

echo
echo "Conventional Gateway Average:"
awk -F, 'NR>1 {sum+=$3} END {print sum/(NR-1) " ms"}' "$CSV"

echo
echo "Conventional App Average:"
awk -F, 'NR>1 {sum+=$4} END {print sum/(NR-1) " ms"}' "$CSV"

echo
echo "Conventional Data-Service Average:"
awk -F, 'NR>1 {sum+=$5} END {print sum/(NR-1) " ms"}' "$CSV"

echo
echo "Provider-First Max Gateway:"
awk -F, 'NR>1 {if($2>max) max=$2} END {print max " ms"}' "$CSV"

echo
echo "Conventional Max Gateway:"
awk -F, 'NR>1 {if($3>max) max=$3} END {print max " ms"}' "$CSV"

echo
echo "Conventional Max App:"
awk -F, 'NR>1 {if($4>max) max=$4} END {print max " ms"}' "$CSV"

echo
echo "Conventional Max Data-Service:"
awk -F, 'NR>1 {if($5>max) max=$5} END {print max " ms"}' "$CSV"

echo
echo "========================================="
