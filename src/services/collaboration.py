"""
实时协作模块
支持多人在线协作创作
"""
import uuid
import time
import json
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class CollaboratorRole(Enum):
    """协作者角色"""
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class ProjectStatus(Enum):
    """项目状态"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Collaborator:
    """协作者"""
    id: str
    username: str
    email: str
    role: CollaboratorRole
    joined_at: float
    last_active: float
    avatar_color: str


@dataclass
class ProjectActivity:
    """项目活动"""
    id: str
    collaborator_id: str
    collaborator_name: str
    action: str
    description: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationProject:
    """协作项目"""
    id: str
    name: str
    description: str
    owner_id: str
    collaborators: List[Collaborator]
    status: ProjectStatus
    created_at: float
    updated_at: float
    activities: List[ProjectActivity] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    song_data: Dict[str, Any] = field(default_factory=dict)


class RealTimeCollaboration:
    """实时协作系统"""
    
    def __init__(self):
        self.projects: Dict[str, CollaborationProject] = {}
        self.active_connections: Dict[str, List[str]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    def create_project(
        self,
        name: str,
        owner_username: str,
        owner_email: str,
        description: str = ""
    ) -> CollaborationProject:
        """
        创建协作项目
        
        Args:
            name: 项目名称
            owner_username: 所有者用户名
            owner_email: 所有者邮箱
            description: 项目描述
            
        Returns:
            协作项目
        """
        project_id = str(uuid.uuid4())
        
        # 创建所有者协作者
        owner = Collaborator(
            id=str(uuid.uuid4()),
            username=owner_username,
            email=owner_email,
            role=CollaboratorRole.OWNER,
            joined_at=time.time(),
            last_active=time.time(),
            avatar_color=self._generate_avatar_color()
        )
        
        # 创建项目
        project = CollaborationProject(
            id=project_id,
            name=name,
            description=description,
            owner_id=owner.id,
            collaborators=[owner],
            status=ProjectStatus.DRAFT,
            created_at=time.time(),
            updated_at=time.time(),
            settings={
                'allow_comments': True,
                'auto_save': True,
                'max_collaborators': 10
            }
        )
        
        self.projects[project_id] = project
        self.active_connections[project_id] = []
        
        # 记录活动
        self._add_activity(
            project,
            owner.id,
            owner.username,
            "创建项目",
            f"创建了项目 '{name}'"
        )
        
        print(f"✅ 项目创建成功: {name} (ID: {project_id})")
        
        return project
    
    def invite_collaborator(
        self,
        project_id: str,
        username: str,
        email: str,
        role: CollaboratorRole = CollaboratorRole.EDITOR
    ) -> Optional[Collaborator]:
        """
        邀请协作者
        
        Args:
            project_id: 项目ID
            username: 用户名
            email: 邮箱
            role: 角色
            
        Returns:
            协作者对象
        """
        project = self.projects.get(project_id)
        if not project:
            print(f"❌ 项目不存在: {project_id}")
            return None
        
        # 检查是否已达到最大协作者数
        if len(project.collaborators) >= project.settings.get('max_collaborators', 10):
            print(f"❌ 项目协作者数量已达上限")
            return None
        
        # 检查是否已是协作者
        for collab in project.collaborators:
            if collab.email == email:
                print(f"❌ {email} 已是协作者")
                return None
        
        # 创建新协作者
        collaborator = Collaborator(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            role=role,
            joined_at=time.time(),
            last_active=time.time(),
            avatar_color=self._generate_avatar_color()
        )
        
        project.collaborators.append(collaborator)
        project.updated_at = time.time()
        
        # 记录活动
        owner = self._get_collaborator_by_id(project, project.owner_id)
        self._add_activity(
            project,
            collaborator.id,
            collaborator.username,
            "加入项目",
            f"{username} 加入了项目"
        )
        
        print(f"✅ 邀请成功: {username} 作为 {role.value}")
        
        return collaborator
    
    def remove_collaborator(
        self,
        project_id: str,
        collaborator_id: str
    ) -> bool:
        """
        移除协作者
        
        Args:
            project_id: 项目ID
            collaborator_id: 协作者ID
            
        Returns:
            是否成功
        """
        project = self.projects.get(project_id)
        if not project:
            return False
        
        # 不能移除所有者
        if collaborator_id == project.owner_id:
            print("❌ 不能移除项目所有者")
            return False
        
        collaborator = self._get_collaborator_by_id(project, collaborator_id)
        if not collaborator:
            return False
        
        project.collaborators.remove(collaborator)
        project.updated_at = time.time()
        
        self._add_activity(
            project,
            collaborator.id,
            collaborator.username,
            "离开项目",
            f"{collaborator.username} 离开了项目"
        )
        
        return True
    
    def update_project_data(
        self,
        project_id: str,
        collaborator_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        更新项目数据
        
        Args:
            project_id: 项目ID
            collaborator_id: 协作者ID
            data: 更新的数据
            
        Returns:
            是否成功
        """
        project = self.projects.get(project_id)
        if not project:
            return False
        
        collaborator = self._get_collaborator_by_id(project, collaborator_id)
        if not collaborator:
            return False
        
        # 检查权限
        if collaborator.role == CollaboratorRole.VIEWER:
            print("❌ 查看者没有编辑权限")
            return False
        
        # 更新数据
        project.song_data.update(data)
        project.updated_at = time.time()
        collaborator.last_active = time.time()
        
        self._add_activity(
            project,
            collaborator.id,
            collaborator.username,
            "更新项目",
            f"更新了项目数据",
            data
        )
        
        # 触发更新事件
        self._emit_event(project_id, 'data_updated', {
            'collaborator_id': collaborator_id,
            'data': data
        })
        
        return True
    
    def get_online_collaborators(self, project_id: str) -> List[Collaborator]:
        """获取在线协作者"""
        return [
            self._get_collaborator_by_id(
                self.projects[project_id],
                collab_id
            )
            for collab_id in self.active_connections.get(project_id, [])
            if self.projects.get(project_id)
        ]
    
    def get_project_history(
        self,
        project_id: str,
        limit: int = 50
    ) -> List[ProjectActivity]:
        """获取项目历史"""
        project = self.projects.get(project_id)
        if not project:
            return []
        
        return sorted(
            project.activities,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
    
    def add_comment(
        self,
        project_id: str,
        collaborator_id: str,
        comment: str,
        position: Dict[str, Any] = None
    ) -> Optional[ProjectActivity]:
        """添加评论"""
        project = self.projects.get(project_id)
        if not project:
            return None
        
        collaborator = self._get_collaborator_by_id(project, collaborator_id)
        if not collaborator:
            return None
        
        activity = ProjectActivity(
            id=str(uuid.uuid4()),
            collaborator_id=collaborator_id,
            collaborator_name=collaborator.username,
            action="添加评论",
            description=comment,
            timestamp=time.time(),
            metadata={'position': position} if position else {}
        )
        
        project.activities.append(activity)
        project.updated_at = time.time()
        
        return activity
    
    def _add_activity(
        self,
        project: CollaborationProject,
        collaborator_id: str,
        collaborator_name: str,
        action: str,
        description: str,
        metadata: Dict[str, Any] = None
    ):
        """添加活动记录"""
        activity = ProjectActivity(
            id=str(uuid.uuid4()),
            collaborator_id=collaborator_id,
            collaborator_name=collaborator_name,
            action=action,
            description=description,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        project.activities.append(activity)
    
    def _get_collaborator_by_id(
        self,
        project: CollaborationProject,
        collaborator_id: str
    ) -> Optional[Collaborator]:
        """根据ID获取协作者"""
        for collab in project.collaborators:
            if collab.id == collaborator_id:
                return collab
        return None
    
    def _generate_avatar_color(self) -> str:
        """生成头像颜色"""
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
        ]
        return colors[int(time.time() * 1000) % len(colors)]
    
    def _emit_event(
        self,
        project_id: str,
        event_type: str,
        data: Dict[str, Any]
    ):
        """触发事件"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(project_id, data)
            except Exception as e:
                print(f"事件处理器错误: {e}")
    
    def on_event(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)


class CollaborationSession:
    """协作会话"""
    
    def __init__(self, collaboration: RealTimeCollaboration):
        self.collaboration = collaboration
        self.project_id: Optional[str] = None
        self.collaborator_id: Optional[str] = None
    
    def join_project(
        self,
        project_id: str,
        username: str,
        email: str
    ) -> bool:
        """加入项目"""
        project = self.collaboration.projects.get(project_id)
        if not project:
            print(f"❌ 项目不存在")
            return False
        
        # 查找现有协作者或邀请新协作者
        collaborator = None
        for collab in project.collaborators:
            if collab.email == email:
                collaborator = collab
                break
        
        if not collaborator:
            collaborator = self.collaboration.invite_collaborator(
                project_id,
                username,
                email,
                CollaboratorRole.EDITOR
            )
        
        if collaborator:
            self.project_id = project_id
            self.collaborator_id = collaborator.id
            
            # 添加到活动连接
            if project_id not in self.collaboration.active_connections:
                self.collaboration.active_connections[project_id] = []
            if collaborator.id not in self.collaboration.active_connections[project_id]:
                self.collaboration.active_connections[project_id].append(collaborator.id)
            
            print(f"✅ {username} 加入了项目 {project.name}")
            return True
        
        return False
    
    def leave_project(self):
        """离开项目"""
        if self.project_id and self.collaborator_id:
            if self.project_id in self.collaboration.active_connections:
                if self.collaborator_id in self.collaboration.active_connections[self.project_id]:
                    self.collaboration.active_connections[self.project_id].remove(
                        self.collaborator_id
                    )
            
            self.project_id = None
            self.collaborator_id = None
    
    def update_data(self, data: Dict[str, Any]) -> bool:
        """更新项目数据"""
        if not self.project_id or not self.collaborator_id:
            return False
        
        return self.collaboration.update_project_data(
            self.project_id,
            self.collaborator_id,
            data
        )


# 全局实例
collaboration_system = RealTimeCollaboration()
