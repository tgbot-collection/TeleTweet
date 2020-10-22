default:
	@echo "Updating codes..."
	git pull
	@echo "Restarting service..."
	systemctl daemon-reload
	systemctl restart TeleTweet
	@echo "You're good to go."
	systemctl status TeleTweet



clean:
	@rm -rf builds
	@rm -f assets.go

