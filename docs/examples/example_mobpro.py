#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pynsee import *


# In[5]:


files = get_file_list()


# In[9]:


files[files['collection'] == 'RP'][['id', 'label']].to_csv('rp.csv')


# In[34]:


col = get_column_metadata('RP_MOBPRO_2016')
col.to_csv('rp_col.csv')


# In[25]:


col[['column', 'column_label_fr']].drop_duplicates()


# In[21]:


col[col['column'] == 'TRANS']


# In[14]:


dfraw = download_file('RP_MOBPRO_2017')


# In[17]:


list_col = ['COMMUNE', 'ARM', 'DCLT']
idf = dfraw[dfraw['REGION'] == '11']


# In[37]:


com = get_geodata('ADMINEXPRESS-COG-CARTO.LATEST:commune')


# In[18]:


idf

