(defun sudo-file ()
  "Open current file with sudo privilege."
  (interactive)
  (let ((file-name (buffer-file-name)))
    (when file-name
      (find-alternate-file (concat "/sudo::" file-name)))))

(defun find-file-sudo (file)
  "Opens FILE with sudo privileges."
  (interactive (list (read-file-name "File: ")))
  (set-buffer (find-file (concat "/sudo::" file))))


(defun sudo (cmd)
  "Run CMD with sudo privileges."
  (interactive "sCmd: ")
  (shell-command (concat
		  "echo "
		  (shell-quote-argument (read-passwd "Password? "))
		  (format " | sudo -S %s" cmd))))

(defun set-directory-rwx (dir)
  "Make DIR read, write and executable for jkitchin."
  (interactive (list (read-directory-name "Directory: ")))
  (sudo (format "setfacl -R -m u:jkitchin:rwx %s" dir)))
