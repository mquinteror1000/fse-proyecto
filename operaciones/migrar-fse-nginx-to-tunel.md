## Migrar fse de nginx oci a un tunel

quitar el certificado y virtual server de nginx

```bash
certbot delete --cert-name fse.mquinteror.net
rm -rf /var/www/fse.mquinteror.net
rm /etc/nginx/conf.d/fse.mquinteror.net.conf
nginx -t && sudo systemctl reload nginx
```


