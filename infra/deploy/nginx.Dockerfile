# syntax=docker/dockerfile:1
FROM nginx:1.25-alpine
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY services/admin/static /var/www/admin/static
EXPOSE 80 443
CMD ["nginx", "-g", "daemon off;"]
