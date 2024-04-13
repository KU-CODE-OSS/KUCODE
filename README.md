# KUCODE (KU COmmunity of DEvelopers)


# Requirements
python >= 3.6  
Node.js >= 18.0  
docker  
docker-compose  

## plugins in vscode
TypeScript Vue Plugin (Volar)   
Vue Language Features (Volar)  
prettier  
Auto Rename Tag  
Auto Close Tag  
Vetur  

# Running
```sh
docker-compose -f docker-compose.base.yaml up -d db
```

### Production
```sh
docker-compose -f docker-compose.base.yaml -f docker-compose.prod.yaml up -d
```
### Production with HTTPS (with Let's Encrypt by Caddy)
> Change HTTPS_DOMAIN environment variable inside __.env__ from localhost to your domain name
```sh
docker-compose -f docker-compose.base.yaml -f docker-compose.prod+ssl.yaml up -d
```
### Development (a hot-reload of Vue.js and Django apps. Celery tasks updated by manual required)
```sh
docker-compose -f docker-compose.base.yaml -f docker-compose.dev.yaml up -d
```
<br />

## 기여 가이드라인
**이 프로젝트에 기여를 하고자 한다면 
[기여 가이드라인](.github/CONTRIBUTING.md) 을 읽어보시기를 바랍니다.**