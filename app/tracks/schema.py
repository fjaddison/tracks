import graphene
from .models import Track, Like
from graphene_django import DjangoObjectType
from users.schema import UserType

class TrackType(DjangoObjectType):
    class Meta:
        model = Track

class Query (graphene.ObjectType):
    tracks = graphene.List(TrackType)

    def resolve_tracks(self, info):
        return Track.objects.all()

class CreateTrack(graphene.Mutation):
    track = graphene.Field(TrackType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()
    # kwargs allows you to bundle all the arguments if the model has a lot of fields
    # you could also just pass them all individually which makes more sense in this case
    # def mutate(self, info, title, description, url)
    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('no user is logged in... log in to add a track')
        # kwargs.get('title')
        track = Track(title=kwargs.get('title'), description=kwargs.get('description'), url=kwargs.get('url'), posted_by=user)
        track.save()

        return CreateTrack(track=track)

class UpdateTrack(graphene.Mutation):
    track = graphene.Field(TrackType)

    class Arguments:
        track_id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    def mutate(self, info, track_id, title, description, url):
        user = info.context.user
        track = Track.objects.get(id=track_id)
        if track.posted_by != user:
            raise Exception('You are not permitted to update this track')
        track.title = title
        track.description = description
        track.url = url
        track.save()
        return UpdateTrack(track=track)

class DeleteTrack(graphene.Mutation):
    track_id = graphene.Int()

    class Arguments:
        track_id = graphene.Int(required=True)
    
    def mutate(self, info, track_id):
        user = info.context.user
        track = Track.objects.get(id=track_id)
        if track.posted_by != user:
            raise Exception('you\'re not allowed to delete this track...')
        track.delete()
        return DeleteTrack(id=track_id)

class CreateLike(graphene.Mutation):
    user = graphene.Field(UserType)
    track = graphene.Field(TrackType)

    class Arguments:
        track_id = graphene.Int(required=True)

    def mutate(self, info, track_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Login to like this track...')
        track = Track.objects.get(id=track_id)
        if not track:
            raise Exception('Can\'t find this track...')
        Like.objects.create(
            user=user, 
            track=track
        )
        return CreateLike(user=user, track=track)

class Mutation(graphene.ObjectType):
    create_track = CreateTrack.Field()
    update_track = UpdateTrack.Field()
    delete_track = DeleteTrack.Field()
    create_like = CreateLike.Field()