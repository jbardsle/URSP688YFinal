#a function to ensure that there are no nulls and that percents are in
#decimal format
def clean_pcts(input):
  input['Hisp_Pct2'] = None
  input.loc[(input['Hisp_Pct'] == 0) | (input['Hisp_Pct'].isnull()), 'Hisp_Pct2'] = 0
  input.loc[input['Hisp_Pct'] > 0, 'Hisp_Pct2'] = input['Hisp_Pct'] / 100
  return input
