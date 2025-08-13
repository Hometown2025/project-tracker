import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MessageCenter = ({ isOpen, onClose }) => {
  const { user, isAdmin, markMessagesAsRead } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      fetchConversations();
      markMessagesAsRead();
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/conversations`);
      setConversations(response.data);
      
      // Auto-select first conversation if any
      if (response.data.length > 0 && !selectedConversation) {
        setSelectedConversation(response.data[0]);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      const response = await axios.get(`${API}/conversations/${conversationId}/messages`);
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || sending) return;

    try {
      setSending(true);
      await axios.post(`${API}/messages`, {
        content: newMessage.trim(),
        recipient_type: isAdmin() ? 'user' : 'admin'
      });

      setNewMessage('');
      
      // Refresh conversations and messages
      await fetchConversations();
      if (selectedConversation) {
        await fetchMessages(selectedConversation.id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const selectConversation = (conversation) => {
    setSelectedConversation(conversation);
    fetchMessages(conversation.id);
    
    // Mark as read
    axios.post(`${API}/conversations/${conversation.id}/mark-read`).catch(console.error);
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatLastMessageTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
      <div className="w-5/6 max-w-6xl h-5/6 bg-white rounded-lg shadow-xl overflow-hidden flex">
        {/* Conversations List */}
        <div className="w-1/3 border-r border-gray-200 flex flex-col">
          <div className="bg-purple-600 text-white p-4 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-xl">💬</span>
              <h2 className="text-lg font-semibold">Messages</h2>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-purple-200 text-xl"
            >
              ×
            </button>
          </div>

          {loading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-gray-500">Loading conversations...</div>
            </div>
          ) : conversations.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500 p-4">
              <span className="text-4xl mb-2">💬</span>
              <p className="text-lg font-medium">No conversations yet</p>
              <p className="text-sm text-center">
                {isAdmin() 
                  ? "Users will see their messages to admins here"
                  : "Start a conversation by sending a message to admins"}
              </p>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => selectConversation(conversation)}
                  className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                    selectedConversation?.id === conversation.id ? 'bg-purple-50 border-l-4 border-l-purple-600' : ''
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <h3 className="font-medium text-sm text-gray-900 truncate">
                      {conversation.title}
                    </h3>
                    {conversation.unread_count_for_user > 0 && (
                      <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1 min-w-[20px] text-center">
                        {conversation.unread_count_for_user}
                      </span>
                    )}
                  </div>
                  {conversation.last_message && (
                    <div className="mt-1">
                      <p className="text-gray-600 text-xs truncate">
                        <span className="font-medium">{conversation.last_message.sender_name}:</span>{' '}
                        {conversation.last_message.content}
                      </p>
                      <p className="text-gray-400 text-xs mt-1">
                        {formatLastMessageTime(conversation.last_message.created_at)}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Messages Area */}
        <div className="flex-1 flex flex-col">
          {selectedConversation ? (
            <>
              {/* Messages Header */}
              <div className="bg-gray-50 p-4 border-b border-gray-200">
                <h3 className="font-medium text-gray-900">{selectedConversation.title}</h3>
                <p className="text-sm text-gray-600">
                  {selectedConversation.participants?.length || 0} participants
                </p>
              </div>

              {/* Messages List */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender_id === user.id ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.sender_id === user.id
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-200 text-gray-900'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm">
                          {message.sender_name}
                        </span>
                        <span
                          className={`text-xs px-2 py-1 rounded-full ${
                            message.sender_role === 'admin'
                              ? 'bg-red-100 text-red-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}
                        >
                          {message.sender_role}
                        </span>
                      </div>
                      <p className="text-sm break-words">{message.content}</p>
                      <p
                        className={`text-xs mt-1 ${
                          message.sender_id === user.id ? 'text-purple-200' : 'text-gray-500'
                        }`}
                      >
                        {formatTime(message.created_at)}
                      </p>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-gray-200">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type your message..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                    disabled={sending}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!newMessage.trim() || sending}
                    className={`px-4 py-2 rounded-lg font-medium ${
                      !newMessage.trim() || sending
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-purple-600 text-white hover:bg-purple-700'
                    }`}
                  >
                    {sending ? '...' : 'Send'}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
              <span className="text-4xl mb-2">💬</span>
              <p className="text-lg font-medium">Select a conversation</p>
              <p className="text-sm">Choose a conversation to start messaging</p>
              {conversations.length === 0 && (
                <button
                  onClick={sendMessage}
                  className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Start New Conversation
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageCenter;