col_dict = {
    'datasetid': 'Dataset ID',
    'recordid': 'Record ID',
    'record_timestamp': 'Record Timestamp',
    'fields.name': 'Station Name',
    'fields.stationcode': 'Station Code',
    'fields.ebike': 'Number of Electric Bicycles',
    'fields.mechanical': 'Number of Mechanical Bicylces',
    'fields.coordonnees_geo': 'Geo. Coordinates',
    'fields.duedate': 'Due Date',
    'fields.numbikesavailable': 'Number of Bicycles Available',
    'fields.numdocksavailable': 'Number of Docks Available for Parking',
    'fields.capacity': 'Capacity',
    'fields.is_renting': 'Is Renting',
    'fields.is_installed': 'Is Installed',
    'fields.nom_arrondissement_communes': 'Name of Arrondisment',
    'fields.is_returning': 'Is Returning',
    'geometry.type': 'Type of Geometry',
    'geometry.coordinates': 'Geometry',
    'percent_numbikesavailable' : 'Percent Capacity (%)',
    'percent_mechanical' : 'Percent of Available as Mechanical',
    'percent_ebike' : 'Percent of Available as Electric',
}

def col_name_to_text(col_name: str)-> str:

    if col_name in col_dict.keys():
        return col_dict[col_name]
    else:
        return col_name