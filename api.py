"""
Instagram Android API Client — Method Reference
Instagram v417.0.0.54.77 · Private API · 90+ endpoints

This file contains the public interface of InstagramClient.
Implementation is available to buyers — contact @trmachabba on Telegram.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


class Device:
    """Android device fingerprint. Pass to InstagramClient."""

    def __init__(self, *, android_id: str = None, device_id: str = None,
                 family_device_id: str = None, phone_id: str = None, **kwargs):
        ...

    @property
    def user_agent(self) -> str:
        ...


class InstagramAPIError(Exception): ...
class LoginRequiredError(InstagramAPIError): ...
class TwoFactorRequired(InstagramAPIError):
    identifier: str
    totp_enabled: bool
    sms_enabled: bool
class CheckpointRequired(InstagramAPIError):
    checkpoint_url: str
class RateLimitError(InstagramAPIError): ...
class AccountBannedError(InstagramAPIError): ...


class InstagramClient:
    """
    Full Instagram Android API client.
    Handles device fingerprinting, attestation tokens (ZCA + USDID),
    all 48 request headers, session persistence, and 90+ API endpoints.
    """

    def __init__(self, device: Device = None, *, mid: str = "",
                 session_file: str = None, proxy: str = None): ...

    def attest(self) -> dict:
        ...

    def login(self, username: str, password: str) -> dict:
        """
        Authenticate with username + password via the Bloks login endpoint.
        """
        ...

    def oauth_token_fetch(self, username: str) -> dict:
        """Bloks OAuth token fetch — post-login token exchange.
        """
        ...

    def submit_2fa_code(
        self,
        code: str,
        two_factor_identifier: str,
        username: str,
        *,
        method: str = "sms",
        waterfall_id: str = None,
    ) -> dict:
        """
        Submit a two-factor authentication OTP code after a TwoFactorRequired error.
        """
        ...

    def resend_2fa_sms(
        self,
        two_factor_identifier: str,
        username: str,
        *,
        waterfall_id: str = None,
    ) -> dict:
        """
        Resend the SMS OTP code for two-factor authentication.
        """
        ...

    def challenge_auto_start(self, checkpoint_url: str) -> dict:
        """
        Begin the account checkpoint/challenge flow.
        """
        ...

    def challenge_submit_code(self, code: str, checkpoint_url: str) -> dict:
        """
        Submit the verification code to complete an account checkpoint challenge.
        """
        ...

    def challenge_select_method(
        self, checkpoint_url: str, method: str = "email"
    ) -> dict:
        """
        Explicitly select a contact-point method for the checkpoint challenge.
        """
        ...

    def challenge_reset(self, checkpoint_url: str) -> dict:
        """
        Reset a challenge (e.g. to restart with a different contact point).
        """
        ...

    def login_with_phone_request_otp(self, phone_number: str) -> dict:
        """
        Request a one-time SMS code for phone-number-based login.
        """
        ...

    def login_with_phone_submit_otp(
        self, phone_number: str, otp_code: str
    ) -> dict:
        """
        Submit the SMS OTP code to complete phone-number-based login.
        """
        ...

    def notif_status(self) -> dict:
        """Bloks notification status — post-login notification opt-in.
        """
        ...

    def bloks_ndx_screen(self) -> dict:
        """POST /bloks/apps/com.instagram.ndx.common.push_ig_ndx_screen/.
        """
        ...

    def user_info(self, user_id: str) -> dict:
        """GET /users/{user_id}/info/ — full user profile.
        """
        ...

    def user_info_stream(self, user_id: str, module: str = "search_typeahead",
                         entry_point: str = "search_navigate_to_user") -> dict:
        """POST /users/{user_id}/info_stream/ — streaming user info.
        """
        ...

    def users_reel_settings(self) -> dict:
        """GET /users/reel_settings/ — story privacy settings.
        """
        ...

    def friendship_show(self, user_id: str) -> dict:
        """GET /friendships/show/{user_id}/ — relationship status.
        """
        ...

    def friendship_show_many(self, user_ids: list[str]) -> dict:
        """POST /friendships/show_many/ — bulk relationship status.
        """
        ...

    def friendship_create(self, user_id: str,
                          container_module: str = "profile") -> dict:
        """POST /friendships/create/{user_id}/ — follow a user.
        """
        ...

    def friendship_destroy(self, user_id: str,
                           container_module: str = "profile") -> dict:
        """POST /friendships/destroy/{user_id}/ — unfollow a user.
        """
        ...

    def friendship_block(self, user_id: str,
                         container_module: str = "profile",
                         surface: str = "profile",
                         is_auto_block_enabled: str = "true") -> dict:
        """POST /friendships/block/{user_id}/ — block a user.
        """
        ...

    def friendship_remove_follower(self, user_id: str,
                                   container_module: str = "profile") -> dict:
        """POST /friendships/remove_follower/{user_id}/ — remove a follower.
        """
        ...

    def friendship_mute_stories(self, user_id: str,
                                source: str = "profile") -> dict:
        """POST /friendships/block_friend_reel/{user_id}/ — mute someone's stories.
        """
        ...

    def friendship_unmute_stories(self, user_id: str,
                                  source: str = "profile") -> dict:
        """POST /friendships/unblock_friend_reel/{user_id}/ — unmute someone's stories.
        """
        ...

    def media_like(self, media_id: str,
                   container_module: str = "feed_contextual_profile") -> dict:
        """POST /media/{media_id}/like/ — like a post.
        """
        ...

    def media_comment(self, media_id: str, comment_text: str,
                      container_module: str = "comments_v2_feed_contextual_profile") -> dict:
        """POST /media/{media_id}/comment/ — post a comment.
        """
        ...

    def media_comment_check_offensive(self, media_id: str,
                                      comment_text: str) -> dict:
        """POST /media/comment/check_offensive_comment/ — pre-check comment.
        """
        ...

    def media_comments(self, media_id: str, min_id: str = None) -> dict:
        """GET /media/{media_id}/stream_comments/ — fetch comments.
        """
        ...

    def media_comment_infos(self, media_ids: list[str]) -> dict:
        """GET /media/comment_infos/ — comment info for multiple media.
        """
        ...

    def media_blocked(self) -> dict:
        """GET /media/blocked/ — list of blocked media IDs.
        """
        ...

    def media_create_note(self, media_id: str, text: str = "",
                          note_style: str = "13",
                          audience: str = "close_friends") -> dict:
        """POST /media/create_note/v2/ — create a note on a post.
        """
        ...

    def media_delete_note(self, note_id: str, media_id: str = "",
                          carousel_media_id: str = "",
                          carousel_index: str = "0") -> dict:
        """POST /media/delete_note/ — delete a note.
        """
        ...

    def media_seen(self, reels: dict,
                   container_module: str = "reel_profile") -> dict:
        """POST /api/v2/media/seen/ — mark stories/reels as seen.
        """
        ...

    def limited_interactions_comments(self, media_id: str) -> dict:
        """GET /limited_interactions/{media_id}/comments/limited_comments/.
        """
        ...

    def story_like(self, media_id: str,
                   container_module: str = "reel_feed_timeline_item_header") -> dict:
        """POST /story_interactions/send_story_like/ — like a story.
        """
        ...

    def user_story(self, user_id: str) -> dict:
        """GET /feed/user/{user_id}/story/ — fetch a user's active stories.
        """
        ...

    def highlights_tray(self, user_id: str) -> dict:
        """GET /highlights/{user_id}/highlights_tray/ — fetch highlights.
        """
        ...

    def direct_inbox(self, limit: int = 15,
                     fetch_reason: str = "initial_snapshot") -> dict:
        """GET /direct_v2/inbox/ — fetch DM inbox.
        """
        ...

    def direct_fetch_inbox_updates(self, thread_timestamps_ms: list[str],
                                   ig_thread_ids: list[str],
                                   cursor_timestamp_ms: str) -> dict:
        """GET /direct_v2/inbox/broadcast/fetch_inbox_updates/.
        """
        ...

    def direct_pending_requests(self) -> dict:
        """GET /direct_v2/async_get_pending_requests_preview/.
        """
        ...

    def direct_has_interop_upgraded(self) -> dict:
        """GET /direct_v2/has_interop_upgraded/.
        """
        ...

    def direct_search_gen_ai_bots(self, num_bots: int = 20) -> dict:
        """GET /direct_v2/search_gen_ai_bots/.
        """
        ...

    def direct_batch_sync_disappearing(self, thread_ids: list[str]) -> dict:
        """POST /direct_v2/batch_sync_disappearing_messages_eligibility/.
        """
        ...

    def direct_send_text(self, recipient_users: list[str], text: str) -> dict:
        """POST /direct_v2/threads/broadcast/text/ — send a DM text.
        """
        ...

    def direct_send_media_share(self, recipient_users: list[str],
                                media_id: str,
                                media_type: str = "photo") -> dict:
        """POST /direct_v2/threads/broadcast/media_share/ — share a post via DM.
        """
        ...

    def direct_send_reel_share(self, recipient_users: list[str],
                               media_id: str, reel_id: str,
                               text: str = "",
                               media_type: str = "video") -> dict:
        """POST /direct_v2/threads/broadcast/reel_share/ — reply to a story via DM.
        """
        ...

    def direct_send_reel_react(self, recipient_users: list[str],
                               media_id: str, reel_id: str,
                               reaction_emoji: str = "\U0001f62e") -> dict:
        """POST /direct_v2/threads/broadcast/reel_react/ — react to a story.
        """
        ...

    def direct_send_generic_share(self, recipient_users: list[str],
                                  share_type: str, json_params: dict,
                                  text: str = "") -> dict:
        """POST /direct_v2/threads/broadcast/generic_share/ — generic share (notes, etc.).
        """
        ...

    def direct_send_photo(self, thread_ids: list[str],
                          attachment_fbid: str,
                          send_attribution: str = "DIRECT_THREAD_COMPOSER_CAMERA_BUTTON") -> dict:
        """POST /direct_v2/threads/broadcast/photo_attachment/ — send a photo.
        """
        ...

    def direct_send_raven(self, thread_ids: list[str],
                          attachment_fbid: str, upload_id: str,
                          view_mode: str = "replayable") -> dict:
        """POST /direct_v2/threads/broadcast/raven_attachment/ — send vanish-mode photo.
        """
        ...

    def feed_timeline(self, reason: str = "cold_start_fetch",
                      max_id: str = None) -> dict:
        """POST /feed/timeline/ — main feed.
        """
        ...

    def feed_user(self, user_id: str, max_id: str = None,
                  count: int = 18) -> dict:
        """GET /feed/user/{user_id}/ — user's media feed (grid).
        """
        ...

    def feed_reels_tray(self, reason: str = "cold_start",
                        page_size: int = 50) -> dict:
        """POST /feed/reels_tray/ — stories tray.
        """
        ...

    def feed_reels_media(self, reel_ids: list[str],
                         source: str = "feed_timeline") -> dict:
        """POST /feed/reels_media_stream/ — fetch full story reels by user IDs.
        """
        ...

    def feed_get_latest_reel_media(self, user_ids: list[str]) -> dict:
        """POST /feed/get_latest_reel_media/ — check who has active stories.
        """
        ...

    def clips_discover(self, seen_reels: list = None,
                       container_module: str = "clips_viewer_clips_tab") -> dict:
        """POST /clips/discover/stream/ — discover reels feed.
        """
        ...

    def clips_discover_social(self,
                              container_module: str = "clips_viewer_friends_lane") -> dict:
        """POST /clips/discover/social/ — social reels feed (friends lane).
        """
        ...

    def clips_items(self, media_ids: list[str],
                    container_module: str = "clips_viewer_direct") -> dict:
        """GET /clips/items/ — fetch specific clips by media IDs.
        """
        ...

    def clips_get_blend_medias(self, blend_id: str,
                               is_prefetch: bool = True) -> dict:
        """POST /clips/get_blend_medias/ — fetch blend medias for a reel.
        """
        ...

    def clips_mid_cards(self, start_position: int = 1,
                        end_position: int = 2) -> dict:
        """POST /clips/mid_cards/ — fetch mid-roll cards for reels.
        """
        ...

    def clips_write_seen_state(self, impressions: list[str]) -> dict:
        """POST /clips/write_seen_state/ — mark reels as seen.
        """
        ...

    def clips_autoplay_configs(self) -> dict:
        """GET /clips/autoplay_configs/ — autoplay configuration.
        """
        ...

    def clips_share_to_fb_config(self) -> dict:
        """GET /clips/user/share_to_fb_config/.
        """
        ...

    def search_recent(self) -> dict:
        """GET /fbsearch/recent_searches/ — recent search history.
        """
        ...

    def search_nullstate(self, search_type: str = "blended") -> dict:
        """GET /fbsearch/nullstate_dynamic_sections/ — search suggestions.
        """
        ...

    def search_register_click(self, entity_id: str,
                              entity_type: str = "user") -> dict:
        """POST /fbsearch/register_recent_search_click/ — log a search click.
        """
        ...

    def tags_search(self, query: str, count: int = 30) -> dict:
        """GET /tags/search/ — search hashtags.
        """
        ...

    def discover_ayml(self, module: str = "self_profile") -> dict:
        """POST /discover/ayml/ — 'accounts you may like' suggestions.
        """
        ...

    def discover_topical_explore(self) -> dict:
        """GET /discover/topical_explore/ — explore page.
        """
        ...

    def discover_chaining(self, target_id: str) -> dict:
        """GET /discover/chaining/ — similar accounts.
        """
        ...

    def accounts_contact_point_prefill(self) -> dict:
        """POST /accounts/contact_point_prefill/.
        """
        ...

    def accounts_current_user(self) -> dict:
        """GET /accounts/current_user/ — current user profile (edit mode).
        """
        ...

    def accounts_set_biography(self, raw_text: str) -> dict:
        """POST /accounts/set_biography/ — update bio.
        """
        ...

    def accounts_set_gender(self, gender: str = "3",
                            custom_gender: str = "") -> dict:
        """POST /accounts/set_gender/ — update gender (1=male, 2=female, 3=prefer not to say).
        """
        ...

    def accounts_process_contact_point_signals(self) -> dict:
        """POST /accounts/process_contact_point_signals/ — post-login signal.
        """
        ...

    def accounts_get_presence_disabled(self) -> dict:
        """GET /accounts/get_presence_disabled/ — activity status setting.
        """
        ...

    def get_account_family(self) -> dict:
        """GET /multiple_accounts/get_account_family/ — linked accounts.
        """
        ...

    def address_book_unlink(self) -> dict:
        """POST /address_book/unlink/ — unlink contacts.
        """
        ...

    def store_push_permissions(self, enabled: bool = True) -> dict:
        """POST /notifications/store_client_push_permissions/.
        """
        ...

    def notifications_get_settings(self,
                                   content_type: str = "instagram_direct") -> dict:
        """GET /notifications/get_notification_settings/.
        """
        ...

    def push_register(self, device_token: str,
                      guid: str = None) -> dict:
        """POST /push/register/ — register device for push notifications.
        """
        ...

    def news_inbox(self) -> dict:
        """GET /news/inbox/ — activity/notifications feed.
        """
        ...

    def get_restricted_users(self) -> dict:
        """GET /restrict_action/get_restricted_users/.
        """
        ...

    def banyan(
        self,
        views: list = None,
        is_private_share: bool = False,
        is_real_time: bool = False,
        ibc_share_sheet_size: int = 5,
    ) -> dict:
        """
        GET /api/v1/banyan/banyan/ — ranked share-sheet recipients.
        """
        ...

    def creator_info(self, user_id: str = None) -> dict:
        """GET /creator/creator_info/ — creator dashboard info.
        """
        ...

    def music_profile(self, user_id: str = None) -> dict:
        """GET /music/profile/{user_id}/ — profile music info.
        """
        ...

    def music_audio_search(self, query: str, count: int = 30) -> dict:
        """GET /music/audio_global_search/ — search music tracks.
        """
        ...

    def music_track_lyrics(self, audio_asset_id: str,
                           audio_cluster_id: str = "") -> dict:
        """GET /music/track/{id}/lyrics/ — fetch lyrics for a track.
        """
        ...

    def live_get_good_time(self) -> dict:
        """POST /live/get_good_time_for_live/ — best time to go live.
        """
        ...

    def creatives_avatar_profile_pic(self, user_id: str = None) -> dict:
        """GET /creatives/avatar_profile_pic/.
        """
        ...

    def creatives_sticker_tray(self, surface: str = "DIRECT",
                               sticker_type: str = "static_stickers") -> dict:
        """POST /creatives/sticker_tray/ — fetch sticker tray.
        """
        ...

    def creatives_write_supported_capabilities(self) -> dict:
        """POST /creatives/write_supported_capabilities/.
        """
        ...

    def graphql_query(self, doc_id: str, variables: dict,
                      friendly_name: str = "") -> dict:
        """POST /graphql/query — generic GraphQL query.
        """
        ...

    def graphql_www(self, doc_id: str, variables: dict,
                    friendly_name: str = "",
                    purpose: str = "fetch") -> dict:
        """POST /graphql_www — GraphQL www query (bloks-backed).
        """
        ...

    def scores_bootstrap_users(self, surfaces: list[str] = None) -> dict:
        """GET /scores/bootstrap/users/ — bootstrap ranking scores.
        """
        ...

    def fundraiser_can_create(self) -> dict:
        """GET /fundraiser/can_create_personal_fundraisers/.
        """
        ...

    def devices_ndx_steps(self,
                          source: str = "NDX_IG_IMMERSIVE") -> dict:
        """GET /devices/ndx/api/async_get_ndx_ig_steps/.
        """
        ...

    def threads_activity_count(self) -> dict:
        """GET /text_feed/ig_text_post_app_new_activity_feed_count/.
        """
        ...

    def zr_dual_tokens(self, fetch_reason: str = "token_expired") -> dict:
        """POST /zr/dual_tokens/ — zero-rating token refresh.
        """
        ...

    def loom_fetch_config(self) -> dict:
        """GET /loom/fetch_config/ — logging/experimentation config.
        """
        ...

    def get_limited_interactions_reminder(self) -> dict:
        """GET /users/get_limited_interactions_reminder/.
        """
        ...

    def direct_send_voice(self, thread_ids: list[str],
                          attachment_fbid: str,
                          waveform: list[float] = None) -> dict:
        """POST /direct_v2/threads/broadcast/voice_attachment/ — send a voice message.
        """
        ...

    def direct_set_media_interventions(self, thread_id: str,
                                       item_id: str, media_id: str,
                                       intervention_type: str = "0") -> dict:
        """POST /direct_v2/threads/{thread_id}/items/{item_id}/set_media_interventions/.
        """
        ...

    def search_account_serp(self, query: str, count: int = 30) -> dict:
        """GET /fbsearch/account_serp/ — user search results page.
        """
        ...

    def search_places(self, query: str, count: int = 30) -> dict:
        """GET /fbsearch/places/ — search places.
        """
        ...

    def ads_async(self, seed_item_id: str,
                  session_time_spent: str = "300") -> dict:
        """POST /ads/async_ads/ — fetch async ads.
        """
        ...

    def launcher_mobileconfig(self,
                              configs: str = "[]",
                              surface_param: str = "198") -> dict:
        """
        POST /api/v1/launcher/mobileconfig/
        """
        ...

    def wwwgraphql_query(self, doc_id: str, variables: dict = None) -> dict:
        """POST /wwwgraphql/ig/query/ — www GraphQL query (different from /graphql/query).
        """
        ...

    def media_configure_to_story(self, upload_id: str, camera_entry_point: str = "story_gallery") -> dict:
        """POST /api/v1/media/configure_to_story/ - Configure uploaded media to story.
        """
        ...

    def accounts_change_profile_picture(self, upload_id: str) -> dict:
        """POST /api/v1/accounts/change_profile_picture/ - Change profile picture.
        """
        ...

    def direct_get_all_channels(self, limit: int = 20) -> dict:
        """
        POST /api/v1/direct_v2/get_all_channels/
        """
        ...

    def direct_get_pending_requests_preview(self) -> dict:
        """GET /api/v1/direct_v2/async_get_pending_requests_preview/ - Get pending DM requests preview.
        """
        ...

    def accounts_fetch_onetap(self) -> dict:
        """POST /api/v1/accounts/fetch_onetap/ - Fetch one-tap login accounts.
        """
        ...

    def feed_injected_reels_media(self, reels: dict) -> dict:
        """POST /api/v1/feed/injected_reels_media/ - Get injected reels media.
        """
        ...

    def upcoming_events_add_event_list(self) -> dict:
        """GET /api/v1/upcoming_events/add_event_list/ - Get upcoming events.
        """
        ...

    def content_scheduling_get_scheduled(self) -> dict:
        """GET /api/v1/content_scheduling/get_scheduled_content/ - Get scheduled content.
        """
        ...

    def live_pre_live_tools(self) -> dict:
        """GET /api/v1/live/pre_live_tools/ - Get pre-live tools.
        """
        ...

    def media_update_pdq_hash(self, media_id: str, pdq_hash: str) -> dict:
        """POST /api/v1/media/update_media_with_pdq_hash_info/ - Update media with PDQ hash.
        """
        ...

    def music_search_session_tracking(self, search_session_id: str) -> dict:
        """POST /api/v1/music/search_session_tracking/ - Track music search session.
        """
        ...

    def warning_check_offensive_multi_text(self, text: str) -> dict:
        """POST /api/v1/warning/check_offensive_multi_text/ - Check for offensive text.
        """
        ...

    def creatives_get_unlockable_sticker_nux(self) -> dict:
        """GET /api/v1/creatives/get_unlockable_sticker_nux/ - Get unlockable sticker NUX.
        """
        ...

    def dynamic_onboarding_get_direct_empty_state(self) -> dict:
        """GET /api/v1/dynamic_onboarding/get_direct_empty_state/ - Get direct empty state.
        """
        ...

    def usertags_feed(self, user_id: str) -> dict:
        """GET /api/v1/usertags/{user_id}/feed/ - Get user tags feed.
        """
        ...

    def pigeon_nest(self, data: dict) -> dict:
        """POST /pigeon_nest - Direct messaging service.
        """
        ...

    def rmd(self, data: dict) -> dict:
        """POST /rmd - Analytics endpoint.
        """
        ...

    def bloks_2fa_has_been_allowed(self, client_input: dict, server_params: dict) -> dict:
        """POST /api/v1/bloks/async_action/com.bloks.www.two_step_verification.has_been_allowed.async/ - 2FA allowed.
        """
        ...

    def search_nullstate_dynamic_sections(self, search_type: str = "blended") -> dict:
        """
        GET /api/v1/fbsearch/nullstate_dynamic_sections/
        """
        ...

    def search_recent_searches(self) -> dict:
        """
        GET /api/v1/fbsearch/recent_searches/
        """
        ...

    def media_stream_comments(
        self,
        media_id: str,
        min_id: Optional[str] = None,
        feed_position: int = 0,
        can_support_threading: bool = True,
        is_carousel_bumped_post: bool = False,
        should_fetch_creator_comment_nudge: bool = True,
    ) -> dict:
        """
        GET /api/v1/media/{media_id}/stream_comments/
        """
        ...

    def feed_reels_media_stream(
        self,
        user_ids: Optional[List[str]] = None,
        exclude_media_ids: Optional[List[str]] = None,
    ) -> dict:
        """
        POST /api/v1/feed/reels_media_stream/
        """
        ...
