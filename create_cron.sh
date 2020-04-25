cd /srv/jitsi

for row in $(jq -c '.[]' /srv/meet-auth/users_to_create.json); do
    _jq() {
       echo ${row} | jq -r ${1}
    }
    sudo docker-compose exec -T prosody prosodyctl --config /config/prosody.cfg.lua register $(_jq '.user') meet.jitsi $(_jq '.password')
done

echo '[]' > /srv/meet-auth/users_to_create.json
