df_30min = yf.download(tickers="GC=F", interval="30m", period="1mo")
df_30min.index.names = ['Timeframe']
df_30min.index.name
df_30min['Date'] = pd.to_datetime(df_30min.index)
df_30min['Date'] = df_30min['Date'].apply(mpl_dates.date2num)
df_30min = df_30min.loc[:,['Date', 'Open', 'High', 'Low', 'Close']]
df_30min = df_30min.reset_index()
df_30min

df_30min['isSL'] = 0
df_30min['isSH'] = 0
df_30min['detection_time'] = 0
pre_S_type = 'n'
pre_SH = 0
pre_SL = 0
pre_SL_index = -1
pre_SH_index = -1


## Function to detect swing lows and swing highs with regards to the instructions described by Lance Beggs.
def which_S(df, j):
    global pre_S_type
    global pre_SL
    global pre_SH
    global pre_SL_index
    global pre_SH_index
    
    support = (
                ((df['Low'][j-3] < df['Low'][j-2]) and (df['Low'][j-3] < df['Low'][j-1]) and \
                (df['Low'][j-3] < df['Low'][j-4]) and (df['Low'][j-3] < df['Low'][j-5])) or \
               (
                ((abs(df['Low'][j-3]-df['Low'][j-4]) < 10) and (df['Low'][j-2]>df['Low'][j-3])\
                 and (df['Low'][j-1]>df['Low'][j-3]) and \
                (df['Low'][j-5]>df['Low'][j-3]) and (df['Low'][j-6]>df['Low'][j-3])) or \
                    
                ((abs(df['Low'][j-3]-df['Low'][j-4]) < 10) and (abs(df['Low'][j-3]-df['Low'][j-5]) < 10)\
                 and (df['Low'][j-2]>df['Low'][j-3]) and (df['Low'][j-1]>df['Low'][j-3]) and \
                (df['Low'][j-6]>df['Low'][j-3]) and (df['Low'][j-7]>df['Low'][j-3])) or \
                
                ((abs(df['Low'][j-3]-df['Low'][j-5]) < 10) and (df['Low'][j-4]>df['Low'][j-3]) \
                 and (df['Low'][j-2]>df['Low'][j-3]) and (df['Low'][j-1]>df['Low'][j-3]) and \
                (df['Low'][j-6]>df['Low'][j-3]) and (df['Low'][j-7]>df['Low'][j-3]))
              )
    )
    
    resistance = (
                ((df['High'][j-3] > df['High'][j-2]) and (df['High'][j-3] > df['High'][j-1]) and \
                (df['High'][j-3] > df['High'][j-4]) and (df['High'][j-3] > df['High'][j-5])) or \
               (
                ((abs(df['High'][j-3]-df['High'][j-4]) < 10) and (df['High'][j-2]<df['High'][j-3]) and \
                 (df['High'][j-1]<df['High'][j-3]) and \
                (df['High'][j-5]<df['High'][j-3]) and (df['High'][j-6]<df['High'][j-3])) or \
                    
                ((abs(df['High'][j-3]-df['High'][j-4]) < 10) and (abs(df['High'][j-3]-df['High'][j-5]) < 10) and \
                 (df['High'][j-2]<df['High'][j-3]) and (df['High'][j-1]<df['High'][j-3]) and \
                (df['High'][j-6]<df['High'][j-3]) and (df['High'][j-7]<df['High'][j-3])) or \
                
                ((abs(df['High'][j-3]-df['High'][j-5]) < 10) and (df['High'][j-4]<df['High'][j-3]) and \
                 (df['High'][j-2]<df['High'][j-3]) and (df['High'][j-1]<df['High'][j-3]) and \
                (df['High'][j-6]<df['High'][j-3]) and (df['High'][j-7]<df['High'][j-3]))
              )
    )
    if support:
        if pre_S_type=='n' or pre_S_type=='H':
            pre_S_type = 'L'
            pre_SL = df['Low'][j-3]
            pre_SL_index = j-3
            df['isSL'][j-3] = 1
            to_append = [df['Timeframe'][j], df['Timeframe'][j-3], df['Low'][j-3], j-3]
            SLs_length = len(SLs)
            SLs.loc[SLs_length] = to_append
            df['detection_time'][j-3] = df['Timeframe'][j]
                       
        elif(pre_S_type=='L' and df['Low'][j-3]<pre_SL):
            pre_SL = df['Low'][j-3]
            df['isSL'][pre_SL_index] = 0
            df['detection_time'][pre_SL_index] = 0
            df['isSL'][j-3] = 1
            df['detection_time'][j-3] = df['Timeframe'][j]
            SLs['SL_value'][df.index[pre_SL_index]] = df['Low'][j-3]
            SLs['CandleNumber'][df.index[pre_SL_index]] = j-3
            pre_SL_index = j-3       
#####################################################################################################        
    elif resistance:
        if pre_S_type=='n' or pre_S_type=='L':
            pre_S_type = 'H'
            pre_SH = df['High'][j-3]
            pre_SH_index = j-3
            df['isSH'][j-3] = 1
            to_append = [df['Timeframe'][j], df['Timeframe'][j-3], df['High'][j-3], j-3]
            SHs_length = len(SHs)
            SHs.loc[SHs_length] = to_append
            df['detection_time'][j-3] = df['Timeframe'][j]
            
        elif (pre_S_type=='H' and df['High'][j-2]>pre_SH):
            pre_SH = df['High'][j-3]
            df['isSH'][pre_SH_index] = 0
            df['detection_time'][pre_SH_index] = 0
            df['isSH'][j-3] = 1
            df['detection_time'][j-3] = df['Timeframe'][j]
            SHs['SH_value'][df.index[pre_SH_index]] = df['High'][j-3]
            SHs['CandleNumber'][df.index[pre_SH_index]] = j-3
            pre_SH_index = j-3
            
## Variables to store swing lows and swing highs.
SHs = pd.DataFrame(columns=['Datetime_know', 'Datetime_actu', 'SH_value', 'CandleNumber'])
SLs = pd.DataFrame(columns=['Datetime_know', 'Datetime_actu', 'SL_value', 'CandleNumber'])

## This loop adds swing highs and swing lows with their detection time to the original dataframe.
for i in range(8, df_30min.shape[0]-2):
    which_S(df_30min, i)
