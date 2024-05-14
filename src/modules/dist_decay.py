#A function to calculate the distance between origin and destination
#parcels and calculate the decay in number of households associated with those parcels
#based on the distance and the selected exponent (1 = linear, 2 = quadratic, etc)
def dist_decay(origins, dest, exp):
  #a dictionary to contain the lists of distances from each polygon
  dict_of_lists = {}
  dict_of_lists_hisp = {}
  for polygon in origins['geometry']:
    #lists to contain the distances from each origin parcel, the number of dwelling units,
    #and the percent Hispanic for each destination parcel
    dist_list = []
    DU_list = []
    HispPct_list = []
    #appends the values for the destination parcel to the lists for each destination
    #parcel
    for point, du, pct in zip(dest['geometry'], dest['DUS'], dest['Hisp_Pct2']):
      dist_list.append(point.distance(polygon))
      DU_list.append(du)
      HispPct_list.append(pct)
    #creates new lists for the weighted values
    dist_list_w = []
    HispPct_w = []
    #locations less than 0.25 miles/402m away will have the value 1
    #while others will decay
    for dist, du, pct in zip(dist_list, DU_list, HispPct_list):
      if dist <= 402:
        dist_list_w.append(1*du)
        HispPct_w.append(1*du*pct)
      elif dist > 402:
        dist_list_w.append(((402/dist)**exp)*du )
        HispPct_w.append(((402/dist)**exp)*du*pct)
    #summing the values for each origin polygon
    dist_list_w_sum = sum(dist_list_w)
    HispPct_w_sum = sum(HispPct_w)
    #creating a new dictionary key, and adding the sum
    #from above as the value
    dict_of_lists[polygon] = dist_list_w_sum
    dict_of_lists_hisp[polygon] = HispPct_w_sum
    #creating a new column that maps the results of the
    #dictionary above by the geometry column
  origins['Customers'] = origins['geometry'].map(dict_of_lists)
  origins['HispCustomers'] = origins['geometry'].map(dict_of_lists_hisp)
  #returns the original table with the new column
  return origins
