# Use cases

# Login
# 1. Successful login with valid username
# 2. Failed login with invalid username
# 3. Failed login with missing username

# List Shipments
# 1. Successful listing of shipments with valid token and no status filter
# 2. Successful listing of shipments with valid token and status filter
# 3. Successful listing of shipments with valid token and date range filter
# 4. Successful listing of shipments with valid token and carrier filter
# 5. Successful listing of shipments with valid token and id filter
# 6. Successful listing of shipments with valid token and multiple filters
# 7. A Global Manager can view all shipments across the state
# 8. A Store Manager can view shipments where their store is either the origin or destination
# 9. A Warehouse Staff can view shipments where their warehouse is either the origin or destination
# 10. A Carrier can view shipments assigned to them
# 11. Failed listing of shipments with invalid token
# 12. Failed listing of shipments with missing token
# 13. Failed listing of shipments with unauthorized role

# Update Shipment
# 1. I can update the status of a shipment to "In Transit" when it is "Created" and the dates are set correctly
# 2. I can update the status of a shipment to "Delivered" when it is "In Transit" and the dates are set correctly
# 3. I cannot update the status of a shipment to "In Transit" when it is already "In Transit"
# 4. I cannot update the status of a shipment to "Delivered" when it is already "Delivered"
# 5. I cannot update the status of a shipment to "Delivered" when it is "Created"
# 6. I can update the location of a shipment when it is "In Transit" and I am the assigned carrier

# Create Shipment
# 1. I can create a shipment with valid data as a Warehouse Staff or Store Manager, only if the origin and destination warehouses are different and the origin warehouse matches my assigned warehouse
# 2. I cannot create a shipment with the same origin and destination warehouses
# 3. I cannot create a shipment with missing required fields
# 4. I cannot create a shipment with invalid warehouse IDs
# 5. I cannot create a shipment if my warehouse does not match the origin warehouse
