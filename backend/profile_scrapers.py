"""
Profile Scrapers for ProfileGPT
Automatically fetch and process profiles from various platforms
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin
import time
from dataclasses import dataclass

@dataclass
class ScrapedProfile:
    platform: str
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    sections: Dict[str, str]

class ProfileScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def detect_platform(self, url: str) -> str:
        """Detect which platform the URL belongs to"""
        domain = urlparse(url).netloc.lower()

        if 'linkedin.com' in domain:
            return 'linkedin'
        elif 'github.com' in domain:
            return 'github'
        elif 'twitter.com' in domain or 'x.com' in domain:
            return 'twitter'
        elif 'dev.to' in domain:
            return 'devto'
        elif 'medium.com' in domain:
            return 'medium'
        elif 'stackoverflow.com' in domain:
            return 'stackoverflow'
        elif 'dribbble.com' in domain:
            return 'dribbble'
        elif 'behance.net' in domain:
            return 'behance'
        else:
            return 'generic'

    def scrape_profile(self, url: str) -> Optional[ScrapedProfile]:
        """Main method to scrape any supported profile"""
        try:
            platform = self.detect_platform(url)

            if platform == 'linkedin':
                return self._scrape_linkedin(url)
            elif platform == 'github':
                return self._scrape_github(url)
            elif platform == 'twitter':
                return self._scrape_twitter(url)
            elif platform == 'devto':
                return self._scrape_devto(url)
            elif platform == 'medium':
                return self._scrape_medium(url)
            elif platform == 'stackoverflow':
                return self._scrape_stackoverflow(url)
            else:
                return self._scrape_generic(url)

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def _scrape_linkedin(self, url: str) -> Optional[ScrapedProfile]:
        """Scrape LinkedIn profile (Note: LinkedIn blocks most scraping)"""
        # LinkedIn heavily blocks scraping, so this is a placeholder
        # In production, you'd need LinkedIn API or special techniques

        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to get basic info from meta tags
            title = self._get_meta_content(soup, 'og:title') or \
                   soup.find('title').get_text() if soup.find('title') else 'LinkedIn Profile'

            description = self._get_meta_content(soup, 'og:description') or \
                         self._get_meta_content(soup, 'description') or ''

            # For demo purposes, create sample content
            content = f"""
LinkedIn Profile: {title}

About: {description}

Note: This is a placeholder for LinkedIn profile content.
LinkedIn restricts automated scraping. In production, this would require:
1. LinkedIn API access
2. User authentication
3. Official data export methods

Skills and Experience would be extracted from the profile sections.
            """.strip()

            return ScrapedProfile(
                platform='linkedin',
                url=url,
                title=title,
                content=content,
                metadata={'description': description, 'platform': 'LinkedIn'},
                sections={'about': description}
            )

        except Exception as e:
            # Return a placeholder profile for demo
            return ScrapedProfile(
                platform='linkedin',
                url=url,
                title='LinkedIn Profile',
                content=f"LinkedIn Profile from: {url}\n\nNote: LinkedIn content extraction requires API access for full functionality.",
                metadata={'platform': 'LinkedIn', 'status': 'limited_access'},
                sections={}
            )

    def _scrape_github(self, url: str) -> Optional[ScrapedProfile]:
        """Scrape GitHub profile"""
        try:
            # Get username from URL
            username = url.rstrip('/').split('/')[-1]

            # Try GitHub API first (no auth needed for public profiles)
            api_url = f"https://api.github.com/users/{username}"
            api_response = self.session.get(api_url, timeout=10)

            content_parts = []
            metadata = {'platform': 'GitHub'}
            sections = {}

            if api_response.status_code == 200:
                user_data = api_response.json()

                title = f"{user_data.get('name', username)} - GitHub Profile"

                # Build content from API data
                content_parts.append(f"# {user_data.get('name', username)}")
                if user_data.get('bio'):
                    content_parts.append(f"**Bio:** {user_data['bio']}")
                    sections['bio'] = user_data['bio']

                if user_data.get('company'):
                    content_parts.append(f"**Company:** {user_data['company']}")

                if user_data.get('location'):
                    content_parts.append(f"**Location:** {user_data['location']}")

                content_parts.append(f"**Public Repositories:** {user_data.get('public_repos', 0)}")
                content_parts.append(f"**Followers:** {user_data.get('followers', 0)}")
                content_parts.append(f"**Following:** {user_data.get('following', 0)}")

                if user_data.get('blog'):
                    content_parts.append(f"**Website:** {user_data['blog']}")

                metadata.update({
                    'username': username,
                    'public_repos': user_data.get('public_repos', 0),
                    'followers': user_data.get('followers', 0),
                    'company': user_data.get('company'),
                    'location': user_data.get('location')
                })

                # Get repositories
                repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10"
                repos_response = self.session.get(repos_url, timeout=10)

                if repos_response.status_code == 200:
                    repos = repos_response.json()
                    content_parts.append("\n## Recent Projects:")

                    repo_info = []
                    for repo in repos[:10]:
                        if not repo.get('fork'):  # Skip forked repos
                            repo_line = f"- **{repo['name']}**: {repo.get('description', 'No description')}"
                            if repo.get('language'):
                                repo_line += f" (Language: {repo['language']})"
                            content_parts.append(repo_line)
                            repo_info.append({
                                'name': repo['name'],
                                'description': repo.get('description'),
                                'language': repo.get('language'),
                                'stars': repo.get('stargazers_count', 0)
                            })

                    sections['projects'] = '\n'.join([f"{r['name']}: {r['description']}" for r in repo_info])
                    metadata['top_repositories'] = repo_info

            else:
                # Fallback to web scraping
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                title = f"{username} - GitHub Profile"

                # Try to get profile info from page
                bio_element = soup.find('div', class_='p-note user-profile-bio')
                if bio_element:
                    bio = bio_element.get_text().strip()
                    content_parts.append(f"**Bio:** {bio}")
                    sections['bio'] = bio

                # Get repository information
                repo_elements = soup.find_all('a', {'data-hovercard-type': 'repository'})
                if repo_elements:
                    content_parts.append("\n## Repositories:")
                    for repo in repo_elements[:10]:
                        repo_name = repo.get_text().strip()
                        content_parts.append(f"- {repo_name}")

            content = '\n'.join(content_parts) if content_parts else f"GitHub Profile: {username}"

            return ScrapedProfile(
                platform='github',
                url=url,
                title=title,
                content=content,
                metadata=metadata,
                sections=sections
            )

        except Exception as e:
            print(f"Error scraping GitHub profile {url}: {e}")
            return None

    def _scrape_devto(self, url: str) -> Optional[ScrapedProfile]:
        """Scrape Dev.to profile"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Get profile info
            title_element = soup.find('h1', class_='crayons-title')
            title = title_element.get_text().strip() if title_element else 'Dev.to Profile'

            # Get bio
            bio_element = soup.find('div', class_='profile-details')
            bio = bio_element.get_text().strip() if bio_element else ''

            content_parts = [f"# {title}"]

            if bio:
                content_parts.append(f"**Bio:** {bio}")

            # Get recent articles
            article_elements = soup.find_all('div', class_='crayons-story')
            if article_elements:
                content_parts.append("\n## Recent Articles:")
                for article in article_elements[:5]:
                    title_link = article.find('h3', class_='crayons-story__title')
                    if title_link:
                        article_title = title_link.get_text().strip()
                        content_parts.append(f"- {article_title}")

            content = '\n'.join(content_parts)

            return ScrapedProfile(
                platform='devto',
                url=url,
                title=title,
                content=content,
                metadata={'platform': 'Dev.to'},
                sections={'bio': bio}
            )

        except Exception as e:
            print(f"Error scraping Dev.to profile {url}: {e}")
            return None

    def _scrape_stackoverflow(self, url: str) -> Optional[ScrapedProfile]:
        """Scrape Stack Overflow profile"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Get user info
            title_element = soup.find('h2', class_='user-card-name')
            title = title_element.get_text().strip() if title_element else 'Stack Overflow Profile'

            content_parts = [f"# {title} - Stack Overflow Profile"]

            # Get reputation
            rep_element = soup.find('div', class_='reputation')
            if rep_element:
                reputation = rep_element.get_text().strip()
                content_parts.append(f"**Reputation:** {reputation}")

            # Get about section
            about_element = soup.find('div', class_='user-about-me')
            if about_element:
                about = about_element.get_text().strip()
                content_parts.append(f"**About:** {about}")

            # Get top tags
            tag_elements = soup.find_all('a', class_='post-tag')
            if tag_elements:
                tags = [tag.get_text().strip() for tag in tag_elements[:10]]
                content_parts.append(f"**Top Tags:** {', '.join(tags)}")

            content = '\n'.join(content_parts)

            return ScrapedProfile(
                platform='stackoverflow',
                url=url,
                title=title,
                content=content,
                metadata={'platform': 'Stack Overflow'},
                sections={'about': about_element.get_text().strip() if about_element else ''}
            )

        except Exception as e:
            print(f"Error scraping Stack Overflow profile {url}: {e}")
            return None

    def _scrape_generic(self, url: str) -> Optional[ScrapedProfile]:
        """Generic web scraper for any URL"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Get title
            title = self._get_meta_content(soup, 'og:title') or \
                   soup.find('title').get_text() if soup.find('title') else 'Web Profile'

            # Get description
            description = self._get_meta_content(soup, 'og:description') or \
                         self._get_meta_content(soup, 'description') or ''

            # Extract main content
            content_parts = [f"# {title}"]

            if description:
                content_parts.append(f"**Description:** {description}")

            # Try to extract meaningful text content
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Limit content length
            if len(text) > 2000:
                text = text[:2000] + "..."

            content_parts.append(f"\n**Content:**\n{text}")
            content = '\n'.join(content_parts)

            return ScrapedProfile(
                platform='web',
                url=url,
                title=title,
                content=content,
                metadata={'platform': 'Web', 'description': description},
                sections={'description': description, 'content': text}
            )

        except Exception as e:
            print(f"Error scraping generic URL {url}: {e}")
            return None

    def _scrape_twitter(self, url: str) -> Optional[ScrapedProfile]:
        """Placeholder for Twitter/X profile scraping"""
        # Twitter/X requires special handling due to API restrictions
        return ScrapedProfile(
            platform='twitter',
            url=url,
            title='Twitter Profile',
            content=f"Twitter Profile: {url}\n\nNote: Twitter profile scraping requires API access.",
            metadata={'platform': 'Twitter', 'status': 'limited_access'},
            sections={}
        )

    def _scrape_medium(self, url: str) -> Optional[ScrapedProfile]:
        """Scrape Medium profile"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Get profile name
            name_element = soup.find('h1')
            title = name_element.get_text().strip() if name_element else 'Medium Profile'

            content_parts = [f"# {title} - Medium Profile"]

            # Get bio
            bio_element = soup.find('h2')
            if bio_element:
                bio = bio_element.get_text().strip()
                content_parts.append(f"**Bio:** {bio}")

            content = '\n'.join(content_parts)

            return ScrapedProfile(
                platform='medium',
                url=url,
                title=title,
                content=content,
                metadata={'platform': 'Medium'},
                sections={'bio': bio if bio_element else ''}
            )

        except Exception as e:
            print(f"Error scraping Medium profile {url}: {e}")
            return None

    def _get_meta_content(self, soup: BeautifulSoup, name: str) -> Optional[str]:
        """Helper to get meta tag content"""
        meta = soup.find('meta', attrs={'name': name}) or \
               soup.find('meta', attrs={'property': name})
        return meta.get('content') if meta else None

# Usage functions for integration with main app

def scrape_profile_from_url(url: str) -> Optional[Dict[str, Any]]:
    """Main function to scrape a profile and return formatted data"""
    scraper = ProfileScraper()
    profile = scraper.scrape_profile(url)

    if profile:
        return {
            'title': profile.title,
            'content': profile.content,
            'platform': profile.platform,
            'url': profile.url,
            'metadata': profile.metadata,
            'sections': profile.sections,
            'source_type': f'{profile.platform}_profile'
        }

    return None

def get_supported_platforms() -> List[Dict[str, str]]:
    """Get list of supported platforms"""
    return [
        {'name': 'GitHub', 'domain': 'github.com', 'example': 'https://github.com/username'},
        {'name': 'Dev.to', 'domain': 'dev.to', 'example': 'https://dev.to/username'},
        {'name': 'Stack Overflow', 'domain': 'stackoverflow.com', 'example': 'https://stackoverflow.com/users/123456/username'},
        {'name': 'Medium', 'domain': 'medium.com', 'example': 'https://medium.com/@username'},
        {'name': 'LinkedIn', 'domain': 'linkedin.com', 'example': 'https://linkedin.com/in/username', 'note': 'Limited access'},
        {'name': 'Twitter/X', 'domain': 'twitter.com', 'example': 'https://twitter.com/username', 'note': 'Limited access'},
        {'name': 'Personal Website', 'domain': 'any', 'example': 'https://yourwebsite.com'},
    ]