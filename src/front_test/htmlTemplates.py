css = '''
<style>
.sidebar .sidebar-content {
        max-width: 100%;
        margin-right: 0;
    }
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #fff;
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://img6.arthub.ai/651bcd22-d464.webp" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
    <br>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://assets.fireside.fm/file/fireside-images/podcasts/images/e/e78a2140-b820-478c-9506-054f2b7e2de2/hosts/3/39b9a9a3-0a20-454c-99b0-2c202023176b/avatar_small.jpg?v=1" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>    
    <div class="message">{{MSG}}</div>
    <br>
</div>
'''
