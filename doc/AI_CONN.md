# AI tools for Connectivity

add_connection - (description)

get_
get_connection_points
- takes list of items e.g. ports, blocks
- point info is X, Y, preferred escape direction (initial direction of wire)
- for port: returns no

get_bitmap(region, scale)

Takes item reference(s) ()


The add_connection tool takes a start position and a series of offsets. To support it the AI must be able to query existing connectivity
- the position of connection points (nodes) on ports and pins
- net by name, or attached port or pin

get_subnet_by_name
- takes name
- returns segments

# get_net

Takes a name, pin reference or port reference. Returns a net reference or none.

# get_net_subnets

Takes a name, pin reference or port reference. Returns a net reference or none.

Returns subnet references.

# get_subnet_nodes





add_connection (insert description)