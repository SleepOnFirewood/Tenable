const options = {
    method: 'GET',
    headers: {
      accept: 'application/json',
      'X-ApiKeys': 'accessKey=;secretKey=' //insert access key and secret key
    }
  };

  let assetNames = new Set([]) //insert values here.
  
  fetch('https://cloud.tenable.com/assets', options)
    .then(response => response.json())
    .then(function(response) {
        for(i=0; i<response['assets'].length; i++)
        {
            let netBios = response['assets'][i]['netbios_name'][0]
            let host = response['assets'][i]['hostname'][0];
            let fqdn = response['assets'][i]['fqdn'][0];
            // console.log(fqdn);
            if(netBios && assetNames.has((response['assets'][i]['netbios_name'][0]).toUpperCase().split('.')[0]))
            {
              console.log('netbios');
              //console.log(response['assets'][i]['netbios_name'])
            }
            else if(host && assetNames.has((response['assets'][i]['hostname'][0]).toUpperCase().split('.')[0]))
            {
              console.log('host');
              //console.log(response['assets'][i]['hostname'])
              
            }
            else if(fqdn)
            {
                for(let k in response['assets'][i]['fqdn'])
                {
                  if (assetNames.has((response['assets'][i]['fqdn'][k]).toUpperCase().split('.')[0]))
                  {
                    console.log('fqdn');
                  // console.log(response['assets'][i]['fqdn'])
                  }
              }
            }
            // else
            // {
            //   console.log('not found')
            // }
        }
        
    }
    )
    .catch(err => console.error(err));
