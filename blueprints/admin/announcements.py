@app.route('/admin/announcements', methods=['GET', 'POST'])
def admin_announcements():
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']

        new_announcement = Announcement(title=title, message=message)
        db.session.add(new_announcement)
        db.session.commit()

        return redirect(url_for('admin_announcements'))

    announcements = Announcement.query.order_by(Announcement.id.desc()).all()
    return render_template('announcements.html', announcements=announcements)