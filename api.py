"""
Instagram Android API Client — Method Reference
Instagram v417.0.0.54.77 · Private API · 90+ endpoints

This file contains the public interface of InstagramClient.
Implementation is available to buyers — contact @TrmaCHABA on Telegram.
https://github.com/Akramelbahar/2026-instagram-android-api-ssl-pinning-v417.0.0.54.77
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
                """
        ...

    def user_info(self, user_id: str) -> dict:
                """
        ...

    def user_info_stream(self, user_id: str, module: str = "search_typeahead",
                         entry_point: str = "search_navigate_to_user") -> dict:
                """
        ...

    def users_reel_settings(self) -> dict:
                """
        ...

    def friendship_show(self, user_id: str) -> dict:
                """
        ...

    def friendship_show_many(self, user_ids: list[str]) -> dict:
                """
        ...

    def friendship_create(self, user_id: str,
                          container_module: str = "profile") -> dict:
                """
        ...

    def friendship_destroy(self, user_id: str,
                           container_module: str = "profile") -> dict:
                """
        ...

    def friendship_block(self, user_id: str,
                         container_module: str = "profile",
                         surface: str = "profile",
                         is_auto_block_enabled: str = "true") -> dict:
                """
        ...

    def friendship_remove_follower(self, user_id: str,
                                   container_module: str = "profile") -> dict:
                """
        ...

    def friendship_mute_stories(self, user_id: str,
                                source: str = "profile") -> dict:
                """
        ...

    def friendship_unmute_stories(self, user_id: str,
                                  source: str = "profile") -> dict:
                """
        ...

    def media_like(self, media_id: str,
                   container_module: str = "feed_contextual_profile") -> dict:
                """
        ...

    def media_comment(self, media_id: str, comment_text: str,
                      container_module: str = "comments_v2_feed_contextual_profile") -> dict:
                """
        ...

    def media_comment_check_offensive(self, media_id: str,
                                      comment_text: str) -> dict:
                """
        ...

    def media_comments(self, media_id: str, min_id: str = None) -> dict:
                """
        ...

    def media_comment_infos(self, media_ids: list[str]) -> dict:
                """
        ...

    def media_blocked(self) -> dict:
                """
        ...

    def media_create_note(self, media_id: str, text: str = "",
                          note_style: str = "13",
                          audience: str = "close_friends") -> dict:
                """
        ...

    def media_delete_note(self, note_id: str, media_id: str = "",
                          carousel_media_id: str = "",
                          carousel_index: str = "0") -> dict:
                """
        ...

    def media_seen(self, reels: dict,
                   container_module: str = "reel_profile") -> dict:
                """
        ...

    def limited_interactions_comments(self, media_id: str) -> dict:
                """
        ...

    def story_like(self, media_id: str,
                   container_module: str = "reel_feed_timeline_item_header") -> dict:
                """
        ...

    def user_story(self, user_id: str) -> dict:
                """
        ...

    def highlights_tray(self, user_id: str) -> dict:
                """
        ...

    def direct_inbox(self, limit: int = 15,
                     fetch_reason: str = "initial_snapshot") -> dict:
                """
        ...

    def direct_fetch_inbox_updates(self, thread_timestamps_ms: list[str],
                                   ig_thread_ids: list[str],
                                   cursor_timestamp_ms: str) -> dict:
                """
        ...

    def direct_pending_requests(self) -> dict:
                """
        ...

    def direct_has_interop_upgraded(self) -> dict:
                """
        ...

    def direct_search_gen_ai_bots(self, num_bots: int = 20) -> dict:
                """
        ...

    def direct_batch_sync_disappearing(self, thread_ids: list[str]) -> dict:
                """
        ...

    def direct_send_text(self, recipient_users: list[str], text: str) -> dict:
                """
        ...

    def direct_send_media_share(self, recipient_users: list[str],
                                media_id: str,
                                media_type: str = "photo") -> dict:
                """
        ...

    def direct_send_reel_share(self, recipient_users: list[str],
                               media_id: str, reel_id: str,
                               text: str = "",
                               media_type: str = "video") -> dict:
                """
        ...

    def direct_send_reel_react(self, recipient_users: list[str],
                               media_id: str, reel_id: str,
                               reaction_emoji: str = "\U0001f62e") -> dict:
                """
        ...

    def direct_send_generic_share(self, recipient_users: list[str],
                                  share_type: str, json_params: dict,
                                  text: str = "") -> dict:
                """
        ...

    def direct_send_photo(self, thread_ids: list[str],
                          attachment_fbid: str,
                          send_attribution: str = "DIRECT_THREAD_COMPOSER_CAMERA_BUTTON") -> dict:
                """
        ...

    def direct_send_raven(self, thread_ids: list[str],
                          attachment_fbid: str, upload_id: str,
                          view_mode: str = "replayable") -> dict:
                """
        ...

    def feed_timeline(self, reason: str = "cold_start_fetch",
                      max_id: str = None) -> dict:
                """
        ...

    def feed_user(self, user_id: str, max_id: str = None,
                  count: int = 18) -> dict:
                """
        ...

    def feed_reels_tray(self, reason: str = "cold_start",
                        page_size: int = 50) -> dict:
                """
        ...

    def feed_reels_media(self, reel_ids: list[str],
                         source: str = "feed_timeline") -> dict:
                """
        ...

    def feed_get_latest_reel_media(self, user_ids: list[str]) -> dict:
                """
        ...

    def clips_discover(self, seen_reels: list = None,
                       container_module: str = "clips_viewer_clips_tab") -> dict:
                """
        ...

    def clips_discover_social(self,
                              container_module: str = "clips_viewer_friends_lane") -> dict:
                """
        ...

    def clips_items(self, media_ids: list[str],
                    container_module: str = "clips_viewer_direct") -> dict:
                """
        ...

    def clips_get_blend_medias(self, blend_id: str,
                               is_prefetch: bool = True) -> dict:
                """
        ...

    def clips_mid_cards(self, start_position: int = 1,
                        end_position: int = 2) -> dict:
                """
        ...

    def clips_write_seen_state(self, impressions: list[str]) -> dict:
                """
        ...

    def clips_autoplay_configs(self) -> dict:
                """
        ...

    def clips_share_to_fb_config(self) -> dict:
                """
        ...

    def search_recent(self) -> dict:
                """
        ...

    def search_nullstate(self, search_type: str = "blended") -> dict:
                """
        ...

    def search_register_click(self, entity_id: str,
                              entity_type: str = "user") -> dict:
                """
        ...

    def tags_search(self, query: str, count: int = 30) -> dict:
                """
        ...

    def discover_ayml(self, module: str = "self_profile") -> dict:
                """
        ...

    def discover_topical_explore(self) -> dict:
                """
        ...

    def discover_chaining(self, target_id: str) -> dict:
                """
        ...

    def accounts_contact_point_prefill(self) -> dict:
                """
        ...

    def accounts_current_user(self) -> dict:
                """
        ...

    def accounts_set_biography(self, raw_text: str) -> dict:
                """
        ...

    def accounts_set_gender(self, gender: str = "3",
                            custom_gender: str = "") -> dict:
                """
        ...

    def accounts_process_contact_point_signals(self) -> dict:
                """
        ...

    def accounts_get_presence_disabled(self) -> dict:
                """
        ...

    def get_account_family(self) -> dict:
                """
        ...

    def address_book_unlink(self) -> dict:
                """
        ...

    def store_push_permissions(self, enabled: bool = True) -> dict:
                """
        ...

    def notifications_get_settings(self,
                                   content_type: str = "instagram_direct") -> dict:
                """
        ...

    def push_register(self, device_token: str,
                      guid: str = None) -> dict:
                """
        ...

    def news_inbox(self) -> dict:
                """
        ...

    def get_restricted_users(self) -> dict:
                """
        ...

    def banyan(
        self,
        views: list = None,
        is_private_share: bool = False,
        is_real_time: bool = False,
        ibc_share_sheet_size: int = 5,
    ) -> dict:
        ...

    def creator_info(self, user_id: str = None) -> dict:
                """
        ...

    def music_profile(self, user_id: str = None) -> dict:
                """
        ...

    def music_audio_search(self, query: str, count: int = 30) -> dict:
                """
        ...

    def music_track_lyrics(self, audio_asset_id: str,
                           audio_cluster_id: str = "") -> dict:
                """
        ...

    def live_get_good_time(self) -> dict:
                """
        ...

    def creatives_avatar_profile_pic(self, user_id: str = None) -> dict:
                """
        ...

    def creatives_sticker_tray(self, surface: str = "DIRECT",
                               sticker_type: str = "static_stickers") -> dict:
                """
        ...

    def creatives_write_supported_capabilities(self) -> dict:
                """
        ...

    def graphql_query(self, doc_id: str, variables: dict,
                      friendly_name: str = "") -> dict:
                """
        ...

    def graphql_www(self, doc_id: str, variables: dict,
                    friendly_name: str = "",
                    purpose: str = "fetch") -> dict:
                """
        ...

    def scores_bootstrap_users(self, surfaces: list[str] = None) -> dict:
                """
        ...

    def fundraiser_can_create(self) -> dict:
                """
        ...

    def devices_ndx_steps(self,
                          source: str = "NDX_IG_IMMERSIVE") -> dict:
                """
        ...

    def threads_activity_count(self) -> dict:
                """
        ...

    def zr_dual_tokens(self, fetch_reason: str = "token_expired") -> dict:
                """
        ...

    def loom_fetch_config(self) -> dict:
                """
        ...

    def get_limited_interactions_reminder(self) -> dict:
                """
        ...

    def direct_send_voice(self, thread_ids: list[str],
                          attachment_fbid: str,
                          waveform: list[float] = None) -> dict:
                """
        ...

    def direct_set_media_interventions(self, thread_id: str,
                                       item_id: str, media_id: str,
                                       intervention_type: str = "0") -> dict:
                """
        ...

    def search_account_serp(self, query: str, count: int = 30) -> dict:
                """
        ...

    def search_places(self, query: str, count: int = 30) -> dict:
                """
        ...

    def ads_async(self, seed_item_id: str,
                  session_time_spent: str = "300") -> dict:
                """
        ...

    def launcher_mobileconfig(self,
                              configs: str = "[]",
                              surface_param: str = "198") -> dict:
        ...

    def wwwgraphql_query(self, doc_id: str, variables: dict = None) -> dict:
                """
        ...

    def media_configure_to_story(self, upload_id: str, camera_entry_point: str = "story_gallery") -> dict:
                """
        ...

    def accounts_change_profile_picture(self, upload_id: str) -> dict:
                """
        ...

    def direct_get_all_channels(self, limit: int = 20) -> dict:
        ...

    def direct_get_pending_requests_preview(self) -> dict:
                """
        ...

    def accounts_fetch_onetap(self) -> dict:
                """
        ...

    def feed_injected_reels_media(self, reels: dict) -> dict:
                """
        ...

    def upcoming_events_add_event_list(self) -> dict:
                """
        ...

    def content_scheduling_get_scheduled(self) -> dict:
                """
        ...

    def live_pre_live_tools(self) -> dict:
                """
        ...

    def media_update_pdq_hash(self, media_id: str, pdq_hash: str) -> dict:
                """
        ...

    def music_search_session_tracking(self, search_session_id: str) -> dict:
                """
        ...

    def warning_check_offensive_multi_text(self, text: str) -> dict:
                """
        ...

    def creatives_get_unlockable_sticker_nux(self) -> dict:
                """
        ...

    def dynamic_onboarding_get_direct_empty_state(self) -> dict:
                """
        ...

    def usertags_feed(self, user_id: str) -> dict:
                """
        ...

    def pigeon_nest(self, data: dict) -> dict:
                """
        ...

    def rmd(self, data: dict) -> dict:
                """
        ...

    def bloks_2fa_has_been_allowed(self, client_input: dict, server_params: dict) -> dict:
                """
        ...

    def search_nullstate_dynamic_sections(self, search_type: str = "blended") -> dict:
        ...

    def search_recent_searches(self) -> dict:
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
        ...

    def feed_reels_media_stream(
        self,
        user_ids: Optional[List[str]] = None,
        exclude_media_ids: Optional[List[str]] = None,
    ) -> dict:
        ...
