aa=`mysql -uwcdb_admin -p2262acef336ce54a  -h 10.126.72.26 -P3261 -BNe  "select ipaddress from db58_wcdb.backup_mongo_status where execution_status=0;"`
echo $aa
