![Anathema Demo](https://raw.githubusercontent.com/firaterror/Anathema/refs/heads/main/Untitledvideo-MadewithClipchamp-ezgif.com-crop.gif)


Subdomatin Takeover scanner I'm building.
Here’s the exact pipeline the tool runs every hour:

```
1. Run subfinder on all top-level domains  
2. Save all discovered subdomains  
3. Run dnsx on the subdomain list  
   - detect NXDOMAIN / SERVFAIL / REFUSED  
   - collect CNAME/NS/rcode responses  
4. Smart mode comparison  
   - new subdomains  
   - removed subdomains  
   - changed DNS state  
5. Run nuclei only where needed  
6. Parse nuclei JSON output  
7. Send notifications

```



This ensures maximum speed + early detection.
